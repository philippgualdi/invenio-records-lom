# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Schemas for OAI."""

from marshmallow import EXCLUDE, Schema, fields, validate


class ExcludeUnknownOrderedSchema(Schema):
    """Schema configured to be ordered and exclude unknown."""

    class Meta:
        """Configuration."""

        ordered = True
        unknown = EXCLUDE


#
# schemas for langstrings (who are annoyingly subtly different)
#
class LangstringXNoneInnerSchema(ExcludeUnknownOrderedSchema):
    """Inner langstring-schema where `language` is set to "x-none"."""

    lang = fields.Constant("x-none")
    text = fields.Str(attribute="#text", data_key="#text", required=True)


class LangstringXNoneSchema(ExcludeUnknownOrderedSchema):
    """Langstring-schema where `langstring.language` is set to "x-none"."""

    langstring = fields.Nested(LangstringXNoneInnerSchema(), required=True)


class LangstringWithLangInnerSchema(ExcludeUnknownOrderedSchema):
    """Inner langstring-schema where `language` is given."""

    # same `lang`-validation as LOM-UIBK
    lang = fields.Str(required=True, validate=validate.Regexp("[a-z][a-z]"))
    text = fields.Str(attribute="#text", data_key="#text", required=True)


class LangstringWithLangSchema(ExcludeUnknownOrderedSchema):
    """Langstring-schema where `langstring.language` is given."""

    langstring = fields.Nested(LangstringWithLangInnerSchema(), required=True)


class LangstringRoleInnerSchema(ExcludeUnknownOrderedSchema):
    """Inner langstring-schema where `#text` is validated to be a LOM role."""

    lang = fields.Str(required=True)
    text = fields.Function(
        str.title,  # called on dump
        str.title,  # called on load
        attribute="#text",
        data_key="#text",
        required=True,
        validate=validate.OneOf(
            [
                "Author",
                "Publisher",
                "Unknown",
                "Initiator",
                "Terminator",
                "Validator",
                "Editor",
                "Graphical Designer",
                "Technical Implementer",
                "Content Provider",
                "Technical Validator",
                "Educational Validator",
                "Script Writer",
                "Instructional Designer",
            ]
        ),
    )


class LangstringRoleSchema(ExcludeUnknownOrderedSchema):
    """Langstring-schema where `langstring.#text` is validated to be a LOM role."""

    langstring = fields.Nested(LangstringRoleInnerSchema(), required=True)


class LangstringLicenseInnerSchema(ExcludeUnknownOrderedSchema):
    """Inner langstring-schema where `lang` is set to "x-t-cc-url"."""

    lang = fields.Constant("x-t-cc-url")
    text = fields.Str(attribute="#text", data_key="#text", required=True)


class LangstringLicenseSchema(ExcludeUnknownOrderedSchema):
    """Langstring-schema where `langstring.lang` is set to "x-t-cc-url"."""

    langstring = fields.Nested(LangstringLicenseInnerSchema(), required=True)


#
# schemas for `general` category
#
class IdentifierSchema(ExcludeUnknownOrderedSchema):
    """Schema for LOM-UIBK's `general.identifier`."""

    catalog = fields.Str()
    entry = fields.Nested(LangstringXNoneSchema())


class GeneralSchema(ExcludeUnknownOrderedSchema):
    """Schema for LOM-UIBK's `general` category."""

    identifier = fields.List(
        fields.Nested(IdentifierSchema()),
        required=True,
        validate=validate.Length(min=1),
    )
    title = fields.Nested(LangstringWithLangSchema(), required=True)
    language = fields.List(fields.Str())
    description = fields.List(fields.Nested(LangstringWithLangSchema()))
    keyword = fields.List(fields.Nested(LangstringWithLangSchema()))
    # TODO: optional field: aggregationlevel


#
# schemas for `lifecycle` category
#
class RoleSchema(ExcludeUnknownOrderedSchema):
    """Schema for LOM-UIBK's `lifecycle.contribute.role`."""

    # pylint: disable=duplicate-code
    source = fields.Field(
        required=True,
        validate=validate.Equal(
            {
                "langstring": {
                    "#text": "LOMv1.0",
                    "lang": "x-none",
                }
            }
        ),
    )
    value = fields.Nested(LangstringRoleSchema(), required=True)


class ContributeSchema(ExcludeUnknownOrderedSchema):
    """Schema for LOM-UIBK's `lifecycle.contribute`."""

    role = fields.Nested(RoleSchema(), required=True)
    centity = fields.Method(
        None,  # dump
        "get_centity",  # load
        data_key="entity",
        required=True,
    )

    def get_centity(self, entities):
        """Get vcard."""
        if not isinstance(entities, list):
            entities = [entities]

        return [
            {
                "vcard": e,  # TODO: fix vcard
            }
            for e in entities
        ]


class LifecycleSchema(ExcludeUnknownOrderedSchema):
    """Schema for LOM-UIBK's `lifecycle` category."""

    version = fields.Field()
    status = fields.Field()
    contribute = fields.List(fields.Nested(ContributeSchema()))


#
# schemas for `technical` category
#
class LocationSchema(ExcludeUnknownOrderedSchema):
    """Schema for LOM-UIBK's `technical.location`."""

    text = fields.Str(attribute="#text", data_key="#text", required=True)


class TechnicalSchema(ExcludeUnknownOrderedSchema):
    """Schema for LOM-UIBK's `technical` category."""

    format = fields.Str(required=True)  # e.g. video/mp4
    # TODO: optional field: size
    location = fields.Nested(LocationSchema(), required=True)
    # TODO: optional field: thumbnail
    # TODO: optional field: duration


#
# schemas for `educational` category
#
class LearningResourceTypeSchema(ExcludeUnknownOrderedSchema):
    """Schema for LOM-UIBK's `educational.learningresourcetype`."""

    # pylint: disable=duplicate-code
    source = fields.Field(
        required=True,
        validate=validate.Equal(
            {
                "langstring": {
                    "#text": "https://w3id.org/kim/hcrt/scheme",
                    "lang": "x-none",
                }
            }
        ),
    )
    id = fields.Str(required=True)


class EducationalSchema(ExcludeUnknownOrderedSchema):
    """Schema for LOM-UIBK's `educational` category."""

    learningresourcetype = fields.Nested(LearningResourceTypeSchema(), required=True)


#
# schemas for `rigths` category
#
class RightsSchema(ExcludeUnknownOrderedSchema):
    """Schema for LOM-UIBK's `rights` category."""

    # TODO: get `copyrightandotherrestrictions`` from passed in obj instead
    copyrightandotherrestrictions = fields.Constant(
        {
            "source": {"langstring": {"#text": "LOMv1.0", "lang": "x-none"}},
            "value": {"langstring": {"#text": "yes", "lang": "x-none"}},
        }
    )
    description = fields.Nested(LangstringLicenseSchema(), required=True)


#
# schemas for `classification` category
#
class PurposeSchema(ExcludeUnknownOrderedSchema):
    """Schema for LOM-UIBK's `classification.purpose`."""

    # pylint: disable=duplicate-code
    source = fields.Field(
        required=True,
        validate=validate.Equal(
            {
                "langstring": {
                    "#text": "LOMv1.0",
                    "lang": "x-none",
                }
            }
        ),
    )
    value = fields.Nested(LangstringXNoneSchema(), required=True)


class TaxonSchema(ExcludeUnknownOrderedSchema):
    """Schema for LOM-UIBK's `classification.taxonpath.taxon`."""

    id = fields.Str(required=True)
    # TODO: optional field: entry


class TaxonpathSchema(ExcludeUnknownOrderedSchema):
    """Schema for LOM-UIBK's `classification.taxonpath`."""

    # pylint: disable=duplicate-code
    source = fields.Field(
        required=True,
        validate=validate.Equal(
            {
                "langstring": {
                    "#text": "https://w3id.org/oerbase/vocabs/oefos2012",
                    "lang": "x-none",
                }
            }
        ),
    )
    taxon = fields.Field()


class ClassificationSchema(ExcludeUnknownOrderedSchema):
    """Schema for LOM-UIBK's `classification` category."""

    purpose = fields.Nested(PurposeSchema(), required=True)
    taxonpath = fields.List(fields.Nested(TaxonpathSchema()), required=True)


#
# main schema
#
class LOMMetadataToOAISchema(ExcludeUnknownOrderedSchema):
    """Schema to reorder fields and exclude unneeded fields."""

    general = fields.Nested(GeneralSchema(), required=True)
    lifecycle = fields.Nested(LifecycleSchema(), required=True)
    # TODO: optional field: metametadata
    technical = fields.Nested(TechnicalSchema(), required=True)
    educational = fields.Nested(EducationalSchema(), required=True)
    rights = fields.Nested(RightsSchema(), required=True)
    # TODO: multiplex different ClassificationSchemas based on their purpose
    classification = fields.List(fields.Nested(ClassificationSchema(), required=True))
