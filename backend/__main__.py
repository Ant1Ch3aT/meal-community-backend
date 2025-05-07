def main() -> None:  # pragma: no cover
    # I've done all of my testing on this.
    from functools import partial
    from sys import argv

    from sanic import Sanic
    from sanic.worker.loader import AppLoader

    from backend.infrastructure.argparser import parse_args
    from backend.infrastructure.config import BackendConfig
    from backend.infrastructure.server import create_app

    backend_config = BackendConfig()

    args = parse_args(argv[1:])
    backend_config.update_with_args(args)

    loader = AppLoader(factory=partial(create_app, backend_config))
    app = loader.load()

    app.prepare(
        backend_config.HOST,
        backend_config.PORT,
        debug=backend_config.DEBUG,
        workers=backend_config.WORKERS,
    )
    Sanic.serve(app, app_loader=loader)


if __name__ == "__main__":  # pragma: no cover
    main()
