#!/usr/bin/env python3
# Apply the experimental SDDM loginToken patch.
# Run this script from the root of an SDDM source tree.
# The script is intentionally conservative and exits if an expected marker is missing.
from pathlib import Path
import re


def read(path):
    return Path(path).read_text()


def write(path, text):
    Path(path).write_text(text)


def find_block_end(s, start):
    brace = s.find('{', start)
    if brace < 0:
        raise SystemExit('opening brace not found')
    depth = 0
    for i in range(brace, len(s)):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return i + 1
    raise SystemExit('block end not found')


def insert_after_line(path, marker, insert):
    s = read(path)
    if insert.strip() in s:
        print(f'already present: {path}')
        return
    lines = s.splitlines(True)
    for i, line in enumerate(lines):
        if marker in line:
            lines.insert(i + 1, insert)
            write(path, ''.join(lines))
            print(f'patched: {path}')
            return
    raise SystemExit(f'marker not found in {path}: {marker}')


def insert_before_line(path, marker, insert):
    s = read(path)
    if insert.strip() in s:
        print(f'already present: {path}')
        return
    lines = s.splitlines(True)
    for i, line in enumerate(lines):
        if marker in line:
            lines.insert(i, insert)
            write(path, ''.join(lines))
            print(f'patched: {path}')
            return
    raise SystemExit(f'marker not found in {path}: {marker}')


def insert_after_function(path, signature_fragment, insert):
    s = read(path)
    if insert.strip() in s:
        print(f'already present: {path}')
        return
    start = s.find(signature_fragment)
    if start < 0:
        raise SystemExit(f'function not found in {path}: {signature_fragment}')
    end = find_block_end(s, start)
    write(path, s[:end] + insert + s[end:])
    print(f'patched: {path}')


def insert_after_case(path, case_marker, insert):
    s = read(path)
    if insert.strip() in s:
        print(f'already present: {path}')
        return
    start = s.find(case_marker)
    if start < 0:
        raise SystemExit(f'case not found in {path}: {case_marker}')
    end = find_block_end(s, start)
    write(path, s[:end] + insert + s[end:])
    print(f'patched: {path}')


def regex_replace(path, pattern, repl):
    s = read(path)
    if repl.strip() in s:
        print(f'already present: {path}')
        return
    s2, n = re.subn(pattern, repl, s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f'pattern not found in {path}')
    write(path, s2)
    print(f'patched: {path}')


def require_source_tree():
    required = [
        'src/common/Messages.h',
        'src/greeter/GreeterProxy.h',
        'src/greeter/GreeterProxy.cpp',
        'src/daemon/SocketServer.h',
        'src/daemon/SocketServer.cpp',
        'src/daemon/Display.h',
        'src/daemon/Display.cpp',
        'src/auth/Auth.h',
        'src/auth/Auth.cpp',
        'src/helper/HelperApp.h',
        'src/helper/HelperApp.cpp',
        'src/helper/backend/PamBackend.cpp',
    ]
    missing = [p for p in required if not Path(p).exists()]
    if missing:
        raise SystemExit('this does not look like the expected SDDM source tree; missing: ' + ', '.join(missing))


def main():
    require_source_tree()
    insert_after_line('src/common/Messages.h', 'Login,', '        LoginToken,\n')
    insert_after_line('src/greeter/GreeterProxy.h', 'void login(const QString &user, const QString &password, const int sessionIndex) const;', '        void loginToken(const QString &user, const int sessionIndex) const;\n')
    insert_after_function('src/greeter/GreeterProxy.cpp', 'void GreeterProxy::login(const QString &user, const QString &password, const int sessionIndex) const', r'''

    void GreeterProxy::loginToken(const QString &user, const int sessionIndex) const {
        if (!d->sessionModel) {
            qCritical() << "Session model is not set.";
            return;
        }
        QModelIndex index = d->sessionModel->index(sessionIndex, 0);
        Session::Type type = static_cast<Session::Type>(d->sessionModel->data(index, SessionModel::TypeRole).toInt());
        QString name = d->sessionModel->data(index, SessionModel::FileRole).toString();
        Session session(type, name);
        SocketWriter(d->socket) << quint32(GreeterMessages::LoginToken) << user << session;
    }
''')
    insert_before_line('src/daemon/SocketServer.h', '    private:', '''        void loginToken(QLocalSocket *socket,
                        const QString &user,
                        const Session &session);

''')
    # Some SDDM versions keep the break outside the Login block. Add an explicit break
    # inside the Login block before inserting the new case to avoid fall-through.
    s_socket = read('src/daemon/SocketServer.cpp')
    s_socket = s_socket.replace('emit login(socket, user, password, session);\n                }', 'emit login(socket, user, password, session);\n                    break;\n                }', 1)
    write('src/daemon/SocketServer.cpp', s_socket)

    insert_after_case('src/daemon/SocketServer.cpp', 'case GreeterMessages::Login:', '''
                case GreeterMessages::LoginToken: {
                    qDebug() << "Message received from greeter: LoginToken";
                    QString user;
                    Session session;
                    input >> user >> session;
                    emit loginToken(socket, user, session);
                    break;
                }
''')
    insert_before_line('src/daemon/Display.h', '    signals:', '''        void loginToken(QLocalSocket *socket,
                        const QString &user,
                        const Session &session);

''')
    regex_replace('src/daemon/Display.h', r'bool startAuth\(\s*const QString &user,\s*const QString &password,\s*const Session &session\s*\);', 'bool startAuth(const QString &user, const QString &password,\n                       const Session &session, const QString &pamService = QString());')
    insert_after_line('src/daemon/Display.cpp', 'connect(m_socketServer, &SocketServer::login, this, &Display::login);', '        connect(m_socketServer, &SocketServer::loginToken, this, &Display::loginToken);\n')
    insert_after_function('src/daemon/Display.cpp', 'void Display::login(QLocalSocket *socket,', '''

    void Display::loginToken(QLocalSocket *socket, const QString &user, const Session &session) {
        m_socket = socket;
        if (user == QLatin1String("sddm")) {
            emit loginFailed(m_socket);
            return;
        }
        startAuth(user, QString(), session, QStringLiteral("sddm-token"));
    }
''')
    regex_replace('src/daemon/Display.cpp', r'bool Display::startAuth\(\s*const QString &user,\s*const QString &password,\s*const Session &session\s*\)', 'bool Display::startAuth(const QString &user, const QString &password, const Session &session, const QString &pamService)')
    insert_after_line('src/daemon/Display.cpp', 'm_auth->setUser(user);', '        if (!pamService.isEmpty())\n            m_auth->setPamService(pamService);\n')
    insert_after_line('src/auth/Auth.h', 'void setUser(const QString &user);', '        void setPamService(const QString &service);\n')
    insert_after_line('src/auth/Auth.cpp', 'QString user { };', '            QString pamService { };\n')
    insert_after_function('src/auth/Auth.cpp', 'void Auth::setUser', '''

    void Auth::setPamService(const QString &service) {
        d->pamService = service;
    }
''')
    insert_after_line('src/auth/Auth.cpp', 'args << QStringLiteral("--user") << d->user;', '\n        if (!d->pamService.isEmpty())\n            args << QStringLiteral("--pam-service") << d->pamService;\n')
    insert_after_line('src/helper/HelperApp.h', 'const QString &user() const;', '        const QString &pamService() const;\n')
    insert_after_line('src/helper/HelperApp.h', 'QString m_user { };', '        QString m_pamService { };\n')
    insert_after_function('src/helper/HelperApp.cpp', 'const QString& HelperApp::user() const', '''

    const QString& HelperApp::pamService() const {
        return m_pamService;
    }
''')
    s = read('src/helper/HelperApp.cpp')
    if 'args.indexOf(QStringLiteral("--pam-service"))' not in s:
        start = s.find('if ((pos = args.indexOf(QStringLiteral("--user"))) >= 0)')
        if start < 0:
            raise SystemExit('could not find --user parser in HelperApp.cpp')
        end = find_block_end(s, start)
        insert = '''

        if ((pos = args.indexOf(QStringLiteral("--pam-service"))) >= 0) {
            if (pos >= args.length() - 1) {
                qCritical() << "This application is not supposed to be executed manually";
                exit(Auth::HELPER_OTHER_ERROR);
                return;
            }
            m_pamService = args[pos + 1];
            if (m_pamService != QLatin1String("sddm-token")) {
                qCritical() << "Refusing unsupported PAM service:" << m_pamService;
                exit(Auth::HELPER_AUTH_ERROR);
                return;
            }
        }
'''
        write('src/helper/HelperApp.cpp', s[:end] + insert + s[end:])
        print('patched: src/helper/HelperApp.cpp parser')
    regex_replace('src/helper/backend/PamBackend.cpp', r'QString service = QStringLiteral\("sddm"\);\s*if \(user == QStringLiteral\("sddm"\) && m_greeter\)\s*service = QStringLiteral\("sddm-greeter"\);\s*else if \(m_autologin\)\s*service = QStringLiteral\("sddm-autologin"\);', '''QString service = m_app->pamService();
        if (service.isEmpty()) {
            service = QStringLiteral("sddm");
            if (user == QStringLiteral("sddm") && m_greeter)
                service = QStringLiteral("sddm-greeter");
            else if (m_autologin)
                service = QStringLiteral("sddm-autologin");
        }''')
    print('SDDM loginToken patch applied. Review git diff before building.')

if __name__ == '__main__':
    main()
