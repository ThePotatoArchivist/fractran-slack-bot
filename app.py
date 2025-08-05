import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import fractran
import traceback
from textwrap import dedent
from parse import parse_factor, parse_factors, parse_fraction, parse_program, parse

# This sample slack application uses SocketMode
# For the companion getting started setup guide, 
# see: https://slack.dev/bolt-python/tutorial/getting-started 

# Initializes your app with your bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

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


def run_execute(ack, say, command, verbose: bool):
    ack()

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
        (''.join(output) if verbose else output[-1]) + \
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

@app.command('/run')
def run(ack, say, command):
    run_execute(ack, say, command, False)

@app.command('/runverbose')
def runverbose(ack, say, command):
    run_execute(ack, say, command, True)


@app.command("/latex")
def latex(ack, say, command):
    ack()
    try:
        fractions = parse_program(command['text'])
      
    except (IndexError, ValueError) as e:
        handle_error(say, e, 'Parsing Error')
        return

    try:
        output = fractran.generate_latex(fractions)
    except Exception as e:
        handle_error(say, e, 'Error')
        return
    
    
    response = dedent(f'''\
        <@{command['user_id']}>
        LaTeX: `{output}`
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
