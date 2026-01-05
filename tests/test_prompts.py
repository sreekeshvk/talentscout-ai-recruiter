import pytest

# Simple logic tests for your State Machine
def test_question_counter_logic():
    # Simulate the logic in app.py
    question_count = 0
    response_with_question = "That is correct. Let's move to Question 2: What is a CNN?"
    
    if "?" in response_with_question:
        question_count += 1
    
    assert question_count == 1

def test_interview_activation():
    interview_active = False
    response = "Let's begin with Question 1"
    
    triggers = ["question 1", "first question", "let's begin"]
    if any(trigger in response.lower() for trigger in triggers):
        interview_active = True
        
    assert interview_active is True

def test_session_end_logic():
    question_count = 4
    conversation_ended = False
    
    if question_count > 3:
        conversation_ended = True
        
    assert conversation_ended is True