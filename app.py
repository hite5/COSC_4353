from application import create_app

app = create_app()

if __name__ == '__main__':
    # Turn of debug when running in production
    app.run()