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

def handle_error(respond, e: Exception, msg: str):
    print(traceback.format_exc())
    response = f'{msg}:\n```{type(e).__name__}: {e}```'
    
    respond(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": response},
            }
        ],
        text=response,
    )


def run_execute(ack, respond, command, verbose: bool):
    ack()

    try:
        fractions, input = parse(command['text'])
      
    except (IndexError, ValueError) as e:
        handle_error(respond, e, 'Parsing Error')
        return

    try:
        output, steps = fractran.execute(input, fractions)
    except Exception as e:
        handle_error(respond, e, 'Execution Error')
        return
    
    response = dedent(f'''\
        >>> *Executor:* <@{command['user_id']}>
        *Input:* `{command['text']}`
        *Output:* ```''') + \
        (''.join(output) if verbose else output[-1]) + \
        dedent(f'''\
        ```
        *Steps:* {steps}
        *Total Fractions:* {len(fractions)}
        ''')

    # say() sends a message to the channel where the event was triggered
    respond(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": response},
            }
        ],
        text=response,
        response_type="in_channel",
    )

@app.command('/run')
def run(ack, respond, command):
    run_execute(ack, respond, command, False)

@app.command('/runverbose')
def runverbose(ack, respond, command):
    run_execute(ack, respond, command, True)


@app.command("/fraclatex")
def latex(ack, respond, command):
    ack()
    try:
        fractions = parse_program(command['text'])
      
    except (IndexError, ValueError) as e:
        handle_error(respond, e, 'Parsing Error')
        return

    try:
        output = fractran.generate_latex(fractions)
    except Exception as e:
        handle_error(respond, e, 'Error')
        return
    
    
    response = dedent(f'''\
        <@{command['user_id']}>
        LaTeX: `{output}`
        ''')

    respond(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": response},
            }
        ],
        text=response,
        response_type="in_channel",
    )


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
