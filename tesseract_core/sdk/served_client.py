# Copyright 2025 Pasteur Labs. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""The interface a running Tesseract presents, however it is being served.

Implemented by :mod:`tesseract_core.sdk.docker_client` for containers and by
:mod:`tesseract_core.sdk.local_client` for subprocesses. Kept apart from both so
that neither client has to import the other to get its base class, and so the
interface stays free of anything either transport needs.
"""

from __future__ import annotations

import abc


class ServedTesseract(abc.ABC):
    """A Tesseract that has been started and can be reached, inspected and stopped.

    Implemented by :class:`~tesseract_core.sdk.docker_client.Container` and by
    :class:`~tesseract_core.sdk.local_client.TesseractProcess`, so callers that
    only need to talk to a Tesseract, read its output or shut it down need not
    know which of the two they hold.

    Deliberately narrow: it promises nothing about separating stdout from stderr,
    since a Tesseract served as a bare process writes both to one file.
    """

    # Provided by subclasses, as a field or a property. Not abstract: a dataclass
    # field without a default does not satisfy an abstract property, and
    # requiring one would force every subclass to wrap its own attribute.
    host_ip: str | None
    host_port: str | None

    @property
    def url(self) -> str:
        """Base URL the Tesseract is serving on."""
        return f"http://{self.host_ip}:{self.host_port}"

    @abc.abstractmethod
    def reload(self) -> None:
        """Read the Tesseract's state again."""

    @abc.abstractmethod
    def is_running(self) -> bool:
        """Whether the Tesseract is running now."""

    @abc.abstractmethod
    def remove(self, force: bool = False) -> None:
        """Dispose of the Tesseract, leaving nothing of it behind.

        Named and shaped after docker-py's ``Container.remove``, down to
        refusing a Tesseract that is still running unless ``force`` is set.
        """

    @abc.abstractmethod
    def wait(self, timeout: float | None = None) -> dict:
        """Wait for the Tesseract to stop, and report the status it stopped with.

        Shaped after docker-py's ``Container.wait``, down to returning a dict
        keyed by ``StatusCode``. Waits for as long as the Tesseract runs unless
        ``timeout`` says otherwise, so ask only about one you expect to have
        stopped -- and before disposing of it, since a Tesseract that is gone can
        no longer be asked.
        """

    @abc.abstractmethod
    def logs(self) -> bytes:
        """Everything the Tesseract has written so far."""

    def diagnose_exit(self, logs: str) -> str:
        """Anything this Tesseract can add about why it stopped running.

        The code it exited with and what it wrote are reported by whoever noticed.
        This is for what remains: a cause the transport can name and the logs
        cannot. Empty by default, for a Tesseract with nothing to add. Takes the
        logs as evidence, not to repeat them.
        """
        del logs
        return ""
