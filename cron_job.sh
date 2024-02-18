#!/bin/bash
SCHEDULE_TIME="03:00"
LAST_RUN_FILE="$HOME/.last_daily_spend_run"

CURRENT_TIME=$(date +%s)

if [[ -f "$LAST_RUN_FILE" ]]; then
    LAST_RUN=$(cat "$LAST_RUN_FILE")
else
    LAST_RUN=0
fi

if [[ $(date -r "$LAST_RUN" +%H) -gt 3 ]]; then
	NEXT_RUN=$(date -j -v+1d -f "%s" "$LAST_RUN" +%Y-%m-%d)
else
	NEXT_RUN=$(date -r "$LAST_RUN" +%Y-%m-%d)
fi

NEXT_RUN=$(date -j -f "%Y-%m-%d %H:%M" "$NEXT_RUN $SCHEDULE_TIME" +%s)

if [[ $CURRENT_TIME -le $NEXT_RUN ]]; then
	$HOME/anaconda3/bin/python $HOME/daily-spend/script.py
	echo $CURRENT_TIME > "$LAST_RUN_FILE"
fi