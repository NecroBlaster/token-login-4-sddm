#include <security/pam_appl.h>
#include <stdio.h>

static int conv_func(int num_msg, const struct pam_message **msg,
                     struct pam_response **resp, void *appdata_ptr) {
    *resp = NULL;
    return PAM_SUCCESS;
}

int main(int argc, char **argv) {
    pam_handle_t *pamh = NULL;
    struct pam_conv conv = { conv_func, NULL };

    const char *service = argc > 1 ? argv[1] : "sddm-token";
    const char *user = argc > 2 ? argv[2] : "example_user";

    int ret = pam_start(service, user, &conv, &pamh);
    if (ret != PAM_SUCCESS) {
        fprintf(stderr, "pam_start: %s\n", pam_strerror(pamh, ret));
        return 1;
    }

    ret = pam_authenticate(pamh, 0);
    if (ret != PAM_SUCCESS) {
        fprintf(stderr, "pam_authenticate: %s\n", pam_strerror(pamh, ret));
        pam_end(pamh, ret);
        return 2;
    }

    ret = pam_acct_mgmt(pamh, 0);
    if (ret != PAM_SUCCESS) {
        fprintf(stderr, "pam_acct_mgmt: %s\n", pam_strerror(pamh, ret));
        pam_end(pamh, ret);
        return 3;
    }

    pam_end(pamh, PAM_SUCCESS);
    printf("PAM OK\n");
    return 0;
}
