import streamlit as st

from database.auth_database import (
    create_user,
    verify_user,
    user_exists,
    reset_password
)


# ============================================================
# PATIENT AUTHENTICATION
# ============================================================

def patient_authentication():

    if "patient_page" not in st.session_state:

        st.session_state.patient_page = "signin"


    # ========================================================
    # SIGN IN
    # ========================================================

    if st.session_state.patient_page == "signin":

        st.title("🏥 Smart Health Monitoring")

        st.subheader("Welcome Back")

        st.markdown("### Sign In")

        username = st.text_input(
            "Username",
            key="patient_login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="patient_login_password"
        )

        if st.button(
            "Sign In",
            type="primary",
            use_container_width=True
        ):

            user = verify_user(
                username,
                password,
                "patient"
            )

            if user:

                st.session_state.patient_logged_in = True
                st.session_state.patient_user = user

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )


        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Create Account",
                use_container_width=True
            ):

                st.session_state.patient_page = "create"
                st.rerun()


        with col2:

            if st.button(
                "Forgot Password?",
                use_container_width=True
            ):

                st.session_state.patient_page = "forgot"
                st.rerun()


        return False


    # ========================================================
    # CREATE ACCOUNT
    # ========================================================

    if st.session_state.patient_page == "create":

        st.title("🏥 Smart Health Monitoring")

        st.subheader("Create Your Account")

        full_name = st.text_input(
            "Full Name",
            key="patient_create_name"
        )

        username = st.text_input(
            "Username",
            key="patient_create_username"
        )

        email = st.text_input(
            "Email",
            key="patient_create_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="patient_create_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="patient_confirm_password"
        )


        if st.button(
            "Create Account",
            type="primary",
            use_container_width=True
        ):

            if not full_name:

                st.error("Please enter your full name.")

            elif not username:

                st.error("Please enter a username.")

            elif not email:

                st.error("Please enter your email.")

            elif not password:

                st.error("Please enter a password.")

            elif password != confirm_password:

                st.error("Passwords do not match.")

            elif len(password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            else:

                success, message = create_user(
                    full_name,
                    username,
                    email,
                    password,
                    "patient"
                )

                if success:

                    st.success(message)

                    st.info(
                        "Your account has been created. "
                        "Please sign in."
                    )

                    st.session_state.patient_page = "signin"

                else:

                    st.error(message)


        if st.button(
            "← Back to Sign In",
            use_container_width=True
        ):

            st.session_state.patient_page = "signin"
            st.rerun()


        return False


    # ========================================================
    # FORGOT PASSWORD
    # ========================================================

    if st.session_state.patient_page == "forgot":

        st.title("🏥 Smart Health Monitoring")

        st.subheader("Forgot Password?")

        username = st.text_input(
            "Username",
            key="patient_forgot_username"
        )

        email = st.text_input(
            "Registered Email",
            key="patient_forgot_email"
        )

        new_password = st.text_input(
            "New Password",
            type="password",
            key="patient_new_password"
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            key="patient_confirm_new_password"
        )


        if st.button(
            "Reset Password",
            type="primary",
            use_container_width=True
        ):

            if not username or not email:

                st.error(
                    "Please enter your username and email."
                )

            elif not new_password:

                st.error(
                    "Please enter a new password."
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(new_password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            else:

                success, message = reset_password(
                    username,
                    email,
                    new_password
                )

                if success:

                    st.success(message)

                    st.session_state.patient_page = "signin"

                else:

                    st.error(message)


        if st.button(
            "← Back to Sign In",
            use_container_width=True
        ):

            st.session_state.patient_page = "signin"
            st.rerun()


        return False


    return False


# ============================================================
# AMBULANCE AUTHENTICATION
# ============================================================

def ambulance_authentication():

    if "ambulance_page" not in st.session_state:

        st.session_state.ambulance_page = "signin"


    # ========================================================
    # SIGN IN
    # ========================================================

    if st.session_state.ambulance_page == "signin":

        st.title("🚑 Ambulance Emergency Response")

        st.subheader("Welcome Back")

        st.markdown("### Sign In")

        username = st.text_input(
            "Username",
            key="ambulance_login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="ambulance_login_password"
        )


        if st.button(
            "Sign In",
            type="primary",
            use_container_width=True
        ):

            user = verify_user(
                username,
                password,
                "ambulance"
            )

            if user:

                st.session_state.ambulance_logged_in = True
                st.session_state.ambulance_user = user

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )


        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Create Account",
                use_container_width=True
            ):

                st.session_state.ambulance_page = "create"
                st.rerun()


        with col2:

            if st.button(
                "Forgot Password?",
                use_container_width=True
            ):

                st.session_state.ambulance_page = "forgot"
                st.rerun()


        return False


    # ========================================================
    # CREATE ACCOUNT
    # ========================================================

    if st.session_state.ambulance_page == "create":

        st.title("🚑 Ambulance Emergency Response")

        st.subheader("Create Ambulance Account")

        full_name = st.text_input(
            "Full Name",
            key="ambulance_create_name"
        )

        username = st.text_input(
            "Username",
            key="ambulance_create_username"
        )

        email = st.text_input(
            "Email",
            key="ambulance_create_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="ambulance_create_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="ambulance_confirm_password"
        )


        if st.button(
            "Create Account",
            type="primary",
            use_container_width=True
        ):

            if not full_name:

                st.error("Please enter your full name.")

            elif not username:

                st.error("Please enter a username.")

            elif not email:

                st.error("Please enter your email.")

            elif not password:

                st.error("Please enter a password.")

            elif password != confirm_password:

                st.error("Passwords do not match.")

            elif len(password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            else:

                success, message = create_user(
                    full_name,
                    username,
                    email,
                    password,
                    "ambulance"
                )

                if success:

                    st.success(message)

                    st.info(
                        "Your account has been created. "
                        "Please sign in."
                    )

                    st.session_state.ambulance_page = "signin"

                else:

                    st.error(message)


        if st.button(
            "← Back to Sign In",
            use_container_width=True
        ):

            st.session_state.ambulance_page = "signin"
            st.rerun()


        return False


    # ========================================================
    # FORGOT PASSWORD
    # ========================================================

    if st.session_state.ambulance_page == "forgot":

        st.title("🚑 Ambulance Emergency Response")

        st.subheader("Forgot Password?")

        username = st.text_input(
            "Username",
            key="ambulance_forgot_username"
        )

        email = st.text_input(
            "Registered Email",
            key="ambulance_forgot_email"
        )

        new_password = st.text_input(
            "New Password",
            type="password",
            key="ambulance_new_password"
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            key="ambulance_confirm_new_password"
        )


        if st.button(
            "Reset Password",
            type="primary",
            use_container_width=True
        ):

            if not username or not email:

                st.error(
                    "Please enter your username and email."
                )

            elif not new_password:

                st.error(
                    "Please enter a new password."
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(new_password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            else:

                success, message = reset_password(
                    username,
                    email,
                    new_password
                )

                if success:

                    st.success(message)

                    st.session_state.ambulance_page = "signin"

                else:

                    st.error(message)


        if st.button(
            "← Back to Sign In",
            use_container_width=True
        ):

            st.session_state.ambulance_page = "signin"
            st.rerun()


        return False


    return False