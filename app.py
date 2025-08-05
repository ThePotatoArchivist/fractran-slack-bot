import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import fractran
import traceback
from collections import defaultdict
from textwrap import dedent

# This sample slack application uses SocketMode
# For the companion getting started setup guide, 
# see: https://slack.dev/bolt-python/tutorial/getting-started 

# Initializes your app with your bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

def parse_factor(frac: str):
    split = frac.split('^')
    return split[0], 1 if len(split) < 2 else int(split[1])

def parse_factors(factors: str):
    return defaultdict(int, dict(parse_factor(c) for c in factors.split('*')))

def parse_fraction(fracstr: str):
    for b in fracstr.split('/'):
        yield parse_factors(b)

def parse(strinput: str):
    *fractions, input = strinput.replace(',', '').split(' ')
    
    return [list(parse_fraction(a)) for a in fractions], parse_factors(input)

def parse_program(strinput: str):
    return [list(parse_fraction(a)) for a in strinput.split(' ')]

def handle_error(say, e: Exception, msg: str):
    print(traceback.format_exc())
    response = f'{msg}:\n```{type(e).__name__}: {e}```'
    
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": response},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Dismiss"},
                    "action_id": "button_click",
                },
            }
        ],
        text=response,
    )


@app.command('/run')
def run_doodle(ack, say, command):
    ack()
    
    error = False

    try:
        fractions, input = parse(command['text'])
      
    except (IndexError, ValueError) as e:
        handle_error(say, e, 'Parsing Error')
        return

    try:
        output, steps = fractran.execute(input, fractions)
    except Exception as e:
        handle_error(say, e, 'Execution Error')
        return
    
    response = dedent(f'''\
        <@{command['user_id']}>
        Input: `{command['text']}`
        Output: ```''') + \
        output + \
        dedent(f'''\
        ```
        Finished in {steps} steps
        Total fractions: {len(fractions)}
        ''')

    # say() sends a message to the channel where the event was triggered
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": response},
            }
        ],
        text=response,
    )

@app.command("/latex")
def latex(ack, say, command):
    ack()
    
    error = False

    try:
        fractions, input = parse(command['text'])
      
    except (IndexError, ValueError) as e:
        handle_error(say, e, 'Parsing Error')
        return

    response = dedent(f'''\
        <@{command['user_id']}>
        LaTeX: `{fractran.generate_latex(fractions)}`
        ''')

    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": response},
            }
        ],
        text=response,
    )
    

@app.action("button_click")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    result = app.client.chat_delete(
        channel=body['container']['channel_id'],
        ts=body['container']['message_ts']
    )
    if not result['ok']:
        print(result)


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
