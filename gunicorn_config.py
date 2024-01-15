def when_ready(_):
    from scripts.cron_setup import setup

    print("Start warming up")
    res = setup()
    print(f"Warmed up with result {res}")
