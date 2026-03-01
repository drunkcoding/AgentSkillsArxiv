# OpenClaw CLI Commands Reference

## Gateway

```bash
openclaw gateway start            # Start the message gateway
openclaw gateway stop             # Stop the gateway
openclaw gateway status           # Show gateway health
```

## Channels

```bash
openclaw channels list                    # List configured channels
openclaw channels pair <channel>          # Pair a new channel (e.g. whatsapp, discord)
openclaw channels unpair <channel>        # Remove a channel
openclaw channels status                  # Quick connectivity check
openclaw channels status --probe          # Deep probe all channels (used by channel_check.sh)
```

## Messages

```bash
openclaw message send --to <id> --channel <ch> --message "text"
openclaw message send --to <id> --channel <ch> --file /path/to/file  # Send attachment
```

## Sessions

```bash
openclaw sessions list                    # List active agent sessions
openclaw sessions kill <session-id>       # Terminate a session
```

## Skills

```bash
openclaw skills list                      # List installed skills
openclaw skills install <path>            # Install skill from path
openclaw skills remove <name>             # Remove a skill
```

## Exec (used by skills)

```bash
openclaw exec <command>                   # Run a command as the agent
```

Skills use `exec` to invoke external scripts like `bridge.py`.

## Environment Variables

| Variable                | Description                        |
|-------------------------|------------------------------------|
| `OPENCLAW_HOME`         | Config directory (default `~/.openclaw`) |
| `OPENCLAW_GATEWAY_PORT` | Gateway listen port (default 8080) |
| `OPENCLAW_LOG_LEVEL`    | Logging verbosity (debug/info/warn/error) |
