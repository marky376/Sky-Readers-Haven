import os
from flask.cli import FlaskGroup
from backend.app import create_app, db


def _get_config_name() -> str:
    """Read desired config or fall back to production."""
    return os.getenv('FLASK_CONFIG', 'production')


def create_cli_app():
    """Factory for CLI usage to avoid flask_script dependency."""
    app = create_app(_get_config_name())

    @app.shell_context_processor
    def _make_shell_context():
        return {'db': db}

    return app


cli = FlaskGroup(create_app=create_cli_app)


if __name__ == '__main__':
    cli()
