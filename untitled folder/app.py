import base64
import random
from pathlib import Path
from typing import Optional
import streamlit as st

st.set_page_config(page_title="Guessing Game")

ASSETS_DIR = Path(__file__).parent / "assets"

def find_first_existing(paths: list[Path]) -> Optional[Path]:
    for path in paths:
        if path.exists():
            return path
    return None


BACKGROUND_IMAGE = find_first_existing(
    [
        ASSETS_DIR / "cat_pondering.png",
        ASSETS_DIR / "cat-pondering-cat.png",
        ASSETS_DIR / "cat_pondering.jpg",
        ASSETS_DIR / "cat_pondering.jpeg",
    ]
)
WIN_IMAGE = find_first_existing(
    [
        ASSETS_DIR / "when_your_educated_guess_is_correct.jpg",
        ASSETS_DIR / "when-your-educated-5ba847.jpg",
        ASSETS_DIR / "when_your_educated_guess_is_correct.png",
    ]
)



def set_global_text_black() -> None:
    st.markdown(
        """
        <style>
        .stApp, .stApp * {
            color: #000000 !important;
        }

        div[data-testid="stButton"] > button,
        div[data-testid="stFormSubmitButton"] > button,
        div[data-testid="stButton"] > button *,
        div[data-testid="stFormSubmitButton"] > button * {
            color: #ffffff !important;
        }

        div[data-testid="stTextInput"] [data-testid="InputInstructions"],
        div[data-testid="stForm"] [data-testid="InputInstructions"],
        [data-testid="InputInstructions"],
        [data-testid="InputInstructions"] * {
            color: #ffffff !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextInput"] textarea {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            caret-color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def set_background_image(image_path: Optional[Path]) -> None:
    if image_path is None or not image_path.exists():
        return

    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    ext = image_path.suffix.lower().replace(".", "") or "png"
    mime = "jpeg" if ext in {"jpg", "jpeg"} else ext
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(
                rgba(255, 255, 255, 0.75),
                rgba(255, 255, 255, 0.75)
            ), url("data:image/{mime};base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_win_meme() -> None:
    if WIN_IMAGE is not None and WIN_IMAGE.exists():
        st.image(str(WIN_IMAGE), caption="When your educated guess is correct")


def init_single_player() -> None:
    if "single_target" not in st.session_state:
        st.session_state.single_target = random.randint(1, 100)
        st.session_state.single_msg = "Guess a number!"
        st.session_state.single_tries = 0
        st.session_state.single_best = None


def reset_vs_computer() -> None:
    st.session_state.vc_user_target = random.randint(1, 100)  # computer's secret for user to guess
    st.session_state.vc_comp_low = 1
    st.session_state.vc_comp_high = 100
    st.session_state.vc_comp_guess = 50
    st.session_state.vc_user_tries = 0
    st.session_state.vc_comp_tries = 0
    st.session_state.vc_over = False
    st.session_state.vc_winner = None
    st.session_state.vc_msg = "Match started. You guess the computer's number."


def next_computer_guess() -> int:
    low = st.session_state.vc_comp_low
    high = st.session_state.vc_comp_high
    return (low + high) // 2


init_single_player()
set_global_text_black()
set_background_image(BACKGROUND_IMAGE)

st.title("🤖 Guessing Game")
mode = st.radio("Select Mode", ["Single Player", "Play vs Computer"], horizontal=True)

if mode == "Single Player":
    with st.form(key="single_form", clear_on_submit=True):
        user_input = st.text_input("Enter number (1-100) and press Enter:")
        submit_single = st.form_submit_button("Submit Guess")

    if submit_single:
        if not user_input:
            st.warning("Please enter a number.")
        elif not user_input.isdigit():
            st.error("Numbers only, please!")
        else:
            guess = int(user_input)
            if not 1 <= guess <= 100:
                st.error("Enter a number between 1 and 100.")
            else:
                st.session_state.single_tries += 1
                if guess < st.session_state.single_target:
                    st.session_state.single_msg = f"📈 {guess} is TOO LOW!"
                elif guess > st.session_state.single_target:
                    st.session_state.single_msg = f"📉 {guess} is TOO HIGH!"
                else:
                    win_tries = st.session_state.single_tries
                    st.session_state.single_msg = f"🎉 YOU GOT IT in {win_tries} tries!"
                    st.balloons()
                    show_win_meme()

                    if (
                        st.session_state.single_best is None
                        or win_tries < st.session_state.single_best
                    ):
                        st.session_state.single_best = win_tries

                    st.session_state.single_target = random.randint(1, 100)
                    st.session_state.single_tries = 0

    col1, col2 = st.columns(2)
    col1.metric("Current Tries", st.session_state.single_tries)
    col2.metric(
        "Best",
        st.session_state.single_best if st.session_state.single_best is not None else "-",
    )
    st.info(st.session_state.single_msg)

else:
    if "vc_over" not in st.session_state:
        reset_vs_computer()

    if st.button("Start New Match", key="reset_vc"):
        reset_vs_computer()

    st.info(st.session_state.vc_msg)

    if not st.session_state.vc_over:
        with st.form(key="vc_user_guess", clear_on_submit=True):
            vc_guess_input = st.text_input("Your guess for the computer's number (1-100):")
            submit_vc_guess = st.form_submit_button("Submit Your Guess")

        if submit_vc_guess:
            if not vc_guess_input:
                st.warning("Please enter a number.")
            elif not vc_guess_input.isdigit():
                st.error("Numbers only, please!")
            else:
                guess = int(vc_guess_input)
                if not 1 <= guess <= 100:
                    st.error("Enter a number between 1 and 100.")
                else:
                    st.session_state.vc_user_tries += 1
                    if guess < st.session_state.vc_user_target:
                        st.session_state.vc_msg = f"Your guess {guess} is too low."
                    elif guess > st.session_state.vc_user_target:
                        st.session_state.vc_msg = f"Your guess {guess} is too high."
                    else:
                        st.session_state.vc_over = True
                        st.session_state.vc_winner = "You"
                        st.session_state.vc_msg = (
                            f"🎉 You win in {st.session_state.vc_user_tries} tries!"
                        )
                        st.balloons()
                        show_win_meme()

        if not st.session_state.vc_over:
            st.write(f"Computer guesses your number: **{st.session_state.vc_comp_guess}**")
            with st.form(key="vc_feedback"):
                fb = st.radio(
                    "Tell computer:",
                    ["Up (my number is higher)", "Down (my number is lower)", "Got it"],
                )
                submit_feedback = st.form_submit_button("Submit Feedback")

            if submit_feedback:
                st.session_state.vc_comp_tries += 1
                guess = st.session_state.vc_comp_guess

                if fb == "Got it":
                    st.session_state.vc_over = True
                    st.session_state.vc_winner = "Computer"
                    st.session_state.vc_msg = (
                        f"Computer wins in {st.session_state.vc_comp_tries} tries."
                    )
                elif fb.startswith("Up"):
                    st.session_state.vc_comp_low = guess + 1
                    if st.session_state.vc_comp_low > st.session_state.vc_comp_high:
                        st.session_state.vc_over = True
                        st.session_state.vc_winner = "Invalid feedback"
                        st.session_state.vc_msg = "Feedback became inconsistent. Start a new match."
                    else:
                        st.session_state.vc_comp_guess = next_computer_guess()
                        st.session_state.vc_msg = (
                            f"Computer will try {st.session_state.vc_comp_guess} next."
                        )
                else:
                    st.session_state.vc_comp_high = guess - 1
                    if st.session_state.vc_comp_low > st.session_state.vc_comp_high:
                        st.session_state.vc_over = True
                        st.session_state.vc_winner = "Invalid feedback"
                        st.session_state.vc_msg = "Feedback became inconsistent. Start a new match."
                    else:
                        st.session_state.vc_comp_guess = next_computer_guess()
                        st.session_state.vc_msg = (
                            f"Computer will try {st.session_state.vc_comp_guess} next."
                        )

    if st.session_state.vc_over and st.session_state.vc_winner:
        st.success(f"Winner: {st.session_state.vc_winner}")

    c1, c2 = st.columns(2)
    c1.metric("Your Tries", st.session_state.vc_user_tries)
    c2.metric("Computer Tries", st.session_state.vc_comp_tries)
