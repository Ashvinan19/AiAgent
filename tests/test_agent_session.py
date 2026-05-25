from google.genai import types

from agent import AgentSession, prepare_turn


def test_prepare_turn_creates_new_session():
    session = prepare_turn(None, "Hello")
    assert len(session.messages) == 1
    assert session.messages[0].parts[0].text == "Hello"
    assert session.modified_project is False
    assert session.verified_after_change is False
    assert session.last_exit_code is None


def test_prepare_turn_appends_to_existing_session():
    session = AgentSession(
        messages=[
            types.Content(
                role="user",
                parts=[types.Part(text="First message")],
            )
        ]
    )
    session.modified_project = True
    session.verified_after_change = True
    session.last_exit_code = 1

    session = prepare_turn(session, "Second message")

    assert len(session.messages) == 2
    assert session.messages[1].parts[0].text == "Second message"
    assert session.modified_project is False
    assert session.verified_after_change is False
    assert session.last_exit_code is None


def test_prepare_turn_preserves_prior_history():
    session = AgentSession()
    prepare_turn(session, "Turn one")
    prepare_turn(session, "Turn two")

    assert len(session.messages) == 2
    assert session.messages[0].parts[0].text == "Turn one"
    assert session.messages[1].parts[0].text == "Turn two"
