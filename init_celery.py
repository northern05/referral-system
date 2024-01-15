def init_celery(celery, application):
    celery.conf.update(application.config["CELERY_CONFIG"])

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""

        app_instance = application

        def __call__(self, *args, **kwargs):
            with application.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
