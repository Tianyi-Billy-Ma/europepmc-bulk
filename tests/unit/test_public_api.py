"""Verify public API surface."""


def test_imports() -> None:
    from europepmc_bulk import (
        AbstractHarvester,
        AnnotationsCollector,
        ArticlesClient,
        Config,
        FTPDownloader,
        HTTPClient,
        OAIUpdater,
        ResumeState,
        __version__,
        atomic_write,
        parse_jats_article,
    )

    assert __version__
    for cls in (
        AbstractHarvester,
        AnnotationsCollector,
        ArticlesClient,
        FTPDownloader,
        OAIUpdater,
        HTTPClient,
        Config,
        ResumeState,
    ):
        assert callable(cls)
    assert callable(atomic_write)
    assert callable(parse_jats_article)
