# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# ZenodoRDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Moderation models."""

from flask import current_app
from invenio_db import db
from invenio_search import current_search_client


class ModerationQuery(db.Model):
    """Moderation queries model."""

    __tablename__ = "moderation_queries"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """Primary key identifier for the moderation query."""

    score = db.Column(db.Integer, default=0)
    """Score associated with the query."""

    query_string = db.Column(db.Text, nullable=False)
    """Query string containing the filter criteria."""

    notes = db.Column(db.Text, nullable=True)
    """Additional notes or comments regarding the moderation query."""

    active = db.Column(db.Boolean, default=True)
    """Indicates whether the moderation query is currently active."""

    @classmethod
    def create(cls, query_string, notes=None, score=0, active=True):
        """Create a new moderation query."""
        query = cls(query_string=query_string, notes=notes, score=score, active=active)
        db.session.add(query)

        try:
            current_search_client.index(
                index="moderation-queries",
                body={
                    "query": {"query_string": {"query": query_string}},
                    "active": active,
                    "score": score,
                    "notes": notes,
                },
            )
        except Exception as e:
            current_app.logger.exception(e)

        return query

    @classmethod
    def get(cls, query_id=None):
        """Retrieve a moderation query by ID or return all queries if no ID is provided."""
        if query_id is not None:
            return cls.query.filter_by(id=query_id).one_or_none()
        return cls.query.all()

    def __repr__(self):
        """Get a string representation of the moderation query."""
        return (
            f"<ModerationQuery id={self.id}, score={self.score}, active={self.active}>"
        )
