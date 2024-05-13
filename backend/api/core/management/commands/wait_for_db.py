
from typing import Any
from django.core.management.base import BaseCommand
from psycopg2 import OperationalError as Psycopg2OpError  # type: ignore
from django.db.utils import OperationalError

import time

class Command(BaseCommand):
  """Django command to wait for database."""
  def handle(self, *args: Any, **options: Any) -> str | None:
    self.stdout.write('Waiting for database...')
    dp_up = False

    while not dp_up:
      try:
        self.check(databases=['default'])
        dp_up = True
      except (Psycopg2OpError, OperationalError):
        self.stdout.write('Database not ready. Retrying...')
        time.sleep(1)

    self.stdout.write(self.style.SUCCESS('Database is ready!'))