# ============================================================
# AI-BASED RISK SCORING
# ============================================================
#
# This module combines multiple monitoring events into a
# project-level risk score.
#
# IMPORTANT:
# This is a software demonstration/risk-prioritization
# mechanism. It is NOT a medical diagnostic system.
# ============================================================


class RiskScoring:

    def __init__(self):

        # ----------------------------------------------------
        # RISK WEIGHTS
        # ----------------------------------------------------

        self.weights = {

            "abnormal_heart_rate": 20,

            "low_spo2": 30,

            "abnormal_temperature": 10,

            "abnormal_blood_pressure": 20,

            "abnormal_inactivity": 20,

            "possible_fall": 25,

            "confirmed_fall": 40
        }


    # ========================================================
    # CALCULATE RISK SCORE
    # ========================================================

    def calculate_score(
        self,
        heart_rate_alert=False,
        spo2_alert=False,
        temperature_alert=False,
        blood_pressure_alert=False,
        inactivity_alert=False,
        possible_fall=False,
        confirmed_fall=False,
        emergency_button=False
    ):

        score = 0

        reasons = []


        # ----------------------------------------------------
        # MANUAL EMERGENCY BUTTON
        # ----------------------------------------------------

        manual_emergency = False

        if emergency_button:

            manual_emergency = True

            reasons.append(
                "Emergency button manually activated"
            )


        # ----------------------------------------------------
        # HEART RATE
        # ----------------------------------------------------

        if heart_rate_alert:

            score += self.weights[
                "abnormal_heart_rate"
            ]

            reasons.append(
                "Abnormal heart rate"
            )


        # ----------------------------------------------------
        # SPO2
        # ----------------------------------------------------

        if spo2_alert:

            score += self.weights[
                "low_spo2"
            ]

            reasons.append(
                "Low SpO2"
            )


        # ----------------------------------------------------
        # TEMPERATURE
        # ----------------------------------------------------

        if temperature_alert:

            score += self.weights[
                "abnormal_temperature"
            ]

            reasons.append(
                "Abnormal temperature"
            )


        # ----------------------------------------------------
        # BLOOD PRESSURE
        # ----------------------------------------------------

        if blood_pressure_alert:

            score += self.weights[
                "abnormal_blood_pressure"
            ]

            reasons.append(
                "Abnormal blood pressure"
            )


        # ----------------------------------------------------
        # INACTIVITY
        # ----------------------------------------------------

        if inactivity_alert:

            score += self.weights[
                "abnormal_inactivity"
            ]

            reasons.append(
                "Abnormal inactivity"
            )


        # ----------------------------------------------------
        # POSSIBLE FALL
        # ----------------------------------------------------

        if possible_fall and not confirmed_fall:

            score += self.weights[
                "possible_fall"
            ]

            reasons.append(
                "Possible fall detected"
            )


        # ----------------------------------------------------
        # CONFIRMED FALL
        # ----------------------------------------------------

        if confirmed_fall:

            score += self.weights[
                "confirmed_fall"
            ]

            reasons.append(
                "Confirmed fall detected"
            )


        # ----------------------------------------------------
        # CAP SCORE
        # ----------------------------------------------------

        score = min(
            score,
            100
        )


        # ----------------------------------------------------
        # DETERMINE RISK LEVEL
        # ----------------------------------------------------

        if score >= 75:

            risk_level = "CRITICAL"

        elif score >= 50:

            risk_level = "HIGH"

        elif score >= 20:

            risk_level = "MODERATE"

        else:

            risk_level = "LOW"


        # ----------------------------------------------------
        # NORMAL CONDITION
        # ----------------------------------------------------

        if not reasons:

            reasons.append(
                "No abnormal conditions detected"
            )


        return {

            "score": score,

            "risk_level": risk_level,

            "reasons": reasons,

            "manual_emergency": manual_emergency

        }


# ============================================================
# FACTORY
# ============================================================

def create_risk_scoring():

    return RiskScoring()


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    risk_engine = RiskScoring()


    print()
    print("=" * 70)
    print("AI RISK SCORING TEST")
    print("=" * 70)


    # --------------------------------------------------------
    # TEST 1 — NORMAL
    # --------------------------------------------------------

    result = risk_engine.calculate_score()

    print()
    print("TEST 1 — NORMAL")
    print(result)


    # --------------------------------------------------------
    # TEST 2 — ABNORMAL INACTIVITY
    # --------------------------------------------------------

    result = risk_engine.calculate_score(
        inactivity_alert=True
    )

    print()
    print("TEST 2 — ABNORMAL INACTIVITY")
    print(result)


    # --------------------------------------------------------
    # TEST 3 — CONFIRMED FALL
    # --------------------------------------------------------

    result = risk_engine.calculate_score(
        confirmed_fall=True
    )

    print()
    print("TEST 3 — CONFIRMED FALL")
    print(result)


    # --------------------------------------------------------
    # TEST 4 — MULTIPLE WARNINGS
    # --------------------------------------------------------

    result = risk_engine.calculate_score(
        heart_rate_alert=True,
        spo2_alert=True,
        inactivity_alert=True,
        confirmed_fall=True
    )

    print()
    print("TEST 4 — MULTIPLE WARNINGS")
    print(result)


    # --------------------------------------------------------
    # TEST 5 — ABNORMAL BLOOD PRESSURE
    # --------------------------------------------------------

    result = risk_engine.calculate_score(
        blood_pressure_alert=True
    )

    print()
    print("TEST 5 — ABNORMAL BLOOD PRESSURE")
    print(result)


    # --------------------------------------------------------
    # TEST 6 — MANUAL EMERGENCY BUTTON
    # --------------------------------------------------------

    result = risk_engine.calculate_score(
        emergency_button=True
    )

    print()
    print("TEST 6 — MANUAL EMERGENCY BUTTON")
    print(result)


    print()
    print("=" * 70)
    print("RISK SCORING TEST COMPLETED")
    print("=" * 70)