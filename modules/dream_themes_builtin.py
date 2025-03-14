"""
Built-in dream themes for the dream story system.
Contains the core dream narratives and choices.
"""

DREAM_THEMES = {
    "falling": {
        "narratives": [
            "You're falling through an endless sky, clouds rushing past you.",
            "The ground approaches rapidly, but you feel strangely calm.",
            "You plummet from a great height, the wind rushing through your hair.",
            "The sensation of falling wakes you with a jolt, but you're still here.",
        ],
        "questions": [
            "Do you try to fly?",
            "Do you accept the fall?",
            "Do you close your eyes?",
            "Do you reach out for something to grab?",
        ],
        "outcomes": {
            "yes": [
                "You spread your arms and begin to glide, the falling transforms into flying.",
                "Your acceptance brings a strange peace as you continue descending.",
                "Darkness envelops you, creating a cocoon of calm in the chaos.",
                "Your hand catches something invisible, stopping your descent instantly.",
            ],
            "no": [
                "You struggle against the inevitable pull downward, tumbling wildly.",
                "Panic sets in as you fight against the fall, your heart racing.",
                "Your eyes remain fixed on the approaching ground, terror mounting.",
                "You curl into yourself, becoming smaller as you continue to fall.",
            ]
        }
    },
    "chase": {
        "narratives": [
            "Something is pursuing you through endless corridors.",
            "Your legs feel heavy as you try to escape what's behind you.",
            "No matter how fast you run, the footsteps behind you stay close.",
            "You hide, holding your breath, as something searches for you.",
        ],
        "questions": [
            "Do you turn to face it?",
            "Do you try to run faster?",
            "Do you call for help?",
            "Do you find a place to hide?",
        ],
        "outcomes": {
            "yes": [
                "You turn, ready to confront your pursuer, but see only shadows.",
                "You push yourself beyond your limits, gaining distance from the threat.",
                "Your voice echoes but someone—or something—responds in the distance.",
                "You discover a perfect hiding spot, tucked away from prying eyes.",
            ],
            "no": [
                "You continue fleeing, the presence behind you growing ever closer.",
                "Your limbs grow heavier, movements becoming sluggish and difficult.",
                "Silence is your only companion as you continue your desperate flight.",
                "Exposed and vulnerable, you keep moving as quietly as possible.",
            ]
        }
    },
    "flying": {
        "narratives": [
            "You're soaring above a landscape of impossible geography.",
            "The sensation of weightlessness fills you with exhilaration.",
            "Wind rushes past as you navigate between towers of cloud.",
            "You hover above your sleeping body, free from physical constraints.",
        ],
        "questions": [
            "Do you fly higher?",
            "Do you look down?",
            "Do you try to reach the horizon?",
            "Do you test your new abilities?",
        ],
        "outcomes": {
            "yes": [
                "You ascend toward the stratosphere, the world becoming tiny below.",
                "Vertigo grips you as you see how far you've come from the ground.",
                "The horizon approaches but seems to extend endlessly before you.",
                "You perform impossible aerial maneuvers, free from physical limitations.",
            ],
            "no": [
                "You maintain your altitude, gliding peacefully through the air.",
                "Your gaze remains fixed ahead, afraid of what looking down might bring.",
                "You circle aimlessly, enjoying the sensation without direction.",
                "You fly cautiously, unsure of the rules governing this strange ability.",
            ]
        }
    },
    "unprepared": {
        "narratives": [
            "You suddenly realize you're in public without proper clothes.",
            "You're taking a test for a class you never attended.",
            "You're performing on stage but don't know any of the lines.",
            "You've arrived at an important meeting completely unprepared.",
        ],
        "questions": [
            "Do you pretend everything is normal?",
            "Do you try to escape the situation?",
            "Do you admit your unpreparedness?",
            "Do you look for help around you?",
        ],
        "outcomes": {
            "yes": [
                "You act with confidence and no one seems to notice anything amiss.",
                "You find an exit, a way out of this embarrassing predicament.",
                "Your honesty is met with unexpected understanding and support.",
                "A friendly face in the crowd nods, offering silent assistance.",
            ],
            "no": [
                "Your discomfort is painfully obvious to everyone around you.",
                "You remain trapped in the situation as anxiety builds.",
                "You fumble forward, trying to hide your lack of preparation.",
                "You stand alone, the weight of expectations crushing you.",
            ]
        }
    },
    "labyrinth": {
        "narratives": [
            "You wander through rooms that impossibly connect to one another.",
            "Doors lead to places that shouldn't exist in the same building.",
            "The hallway extends and contracts as you walk through it.",
            "You recognize this place, but everything is slightly wrong.",
        ],
        "questions": [
            "Do you try to map the impossible space?",
            "Do you follow the strange logic of this place?",
            "Do you look for someone else caught in this maze?",
            "Do you close your eyes and trust intuition?",
        ],
        "outcomes": {
            "yes": [
                "Patterns emerge in the chaos, revealing a hidden order to the space.",
                "By accepting the dream logic, the pathways begin to make sense to you.",
                "You spot another figure in the distance, also searching for a way out.",
                "With eyes closed, your feet carry you confidently forward.",
            ],
            "no": [
                "The more you try to apply reason, the more chaotic the space becomes.",
                "You fight against the dream's rules, becoming more disoriented.",
                "Isolation presses in as you wander the shifting corridors alone.",
                "You stumble forward, eyes open but unseeing of the true path.",
            ]
        }
    },
    "teeth": {
        "narratives": [
            "Your teeth begin to crumble and fall out one by one.",
            "You feel a loose tooth, then another, and another.",
            "Something is wrong with your mouth—teeth shifting and breaking.",
            "You run your tongue over your teeth and feel them disintegrating.",
        ],
        "questions": [
            "Do you try to save the remaining teeth?",
            "Do you seek a mirror to examine yourself?",
            "Do you ask someone nearby for help?",
            "Do you accept this transformation?",
        ],
        "outcomes": {
            "yes": [
                "You cup your hands, collecting the fallen pieces of yourself.",
                "Your reflection reveals something unexpected about your true nature.",
                "A stranger approaches, offering mysterious advice about your condition.",
                "The discomfort fades as you allow yourself to change and transform.",
            ],
            "no": [
                "More teeth loosen and fall, an unstoppable cascade of loss.",
                "You avoid your reflection, afraid of what you might see.",
                "You suffer in isolation, unwilling to reveal your vulnerability.",
                "You fight the change, causing greater pain and discomfort.",
            ]
        }
    }
}
