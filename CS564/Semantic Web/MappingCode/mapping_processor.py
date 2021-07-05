#!/usr/bin/env python3
import sys
sys.dont_write_bytecode = True

import os
from argparse import ArgumentParser

import utilities


class MappingProcessor(object):
    def __init__(self, json_file):
        self.json_file = json_file
        self.map_linked_art_to_schema()

    def map_linked_art_to_schema(self):
        linked_art = utilities.json_to_dict(self.json_file)
        schema_org_entries = []

        set_names(linked_art, schema_org_entries)

        for key, value in linked_art.items():
            if key == "classified_as":
                set_artform(value, linked_art, schema_org_entries)

            set_creator(key, value, linked_art, schema_org_entries)

            if "timespan" in value:
                set_date_created(linked_art[key]["timespan"], schema_org_entries)

            set_location_created(value, schema_org_entries)

        set_main_entity(linked_art, schema_org_entries)

        set_content_location(linked_art, schema_org_entries)

        set_same_as(linked_art, schema_org_entries)

        set_url(linked_art, schema_org_entries)

        set_description(linked_art, schema_org_entries)

        set_dimensions(linked_art, schema_org_entries)

        set_art_materials(linked_art, schema_org_entries)

        utilities.create_file(os.path.join(os.path.dirname(__file__), "SchemaOrg", os.path.basename(self.json_file)),
                              content=format_schema_org_content(linked_art["type"], schema_org_entries))


def format_jsonld_entry(key, value):
    return f'  "{key}": "{value}"'


def set_description(linked_art, schema_org_entries):
    if linked_art.get("referred_to_by", [{}])[0].get("classified_as", [{}])[0].get("_label", "") == "Description":
        schema_org_entries.append(format_jsonld_entry("description",
                                                      linked_art["referred_to_by"][0]["content"]))


def set_url(linked_art, schema_org_entries):
    if linked_art.get("shows", [{}])[0].get("id"):
        schema_org_entries.append(format_jsonld_entry("url", (linked_art["shows"][0]["id"])))
    elif linked_art.get("shown_by", [{}])[0].get("id"):
        schema_org_entries.append(format_jsonld_entry("url", (linked_art["shown_by"][0]["id"])))


def set_same_as(linked_art, schema_org_entries):
    if linked_art.get("equivalent"):
        schema_org_entries.append(format_jsonld_entry("sameAs", linked_art["equivalent"][0]["id"]))


def set_content_location(linked_art, schema_org_entries):
    if linked_art.get("represents", [{}])[0].get("type", "") == "Place":
        schema_org_entries.append(format_jsonld_entry("contentLocation", linked_art["represents"][0]["_label"]))


def set_main_entity(linked_art, schema_org_entries):
    if linked_art.get("represents_instance_of_type", [{}])[0]:
        schema_org_entries.append(format_jsonld_entry("mainEntity",
                                                      linked_art["represents_instance_of_type"][0]["_label"]))


def set_location_created(value, schema_org_entries):
    if "took_place_at" in value:
        if value.get("took_place_at", [{}])[0].get("type", "") == "Place":
            schema_org_entries.append(format_jsonld_entry("locationCreated",
                                                          value["took_place_at"][0]["_label"]))


def set_date_created(timespan, schema_org_entries):
    creation_date = timespan.get("_label",
                                 timespan.get("identified_by", [{}])[0].get("content"))
    schema_org_entries.append(format_jsonld_entry("dateCreated", creation_date.split("-")[1]))


def set_artform(value, linked_art, schema_org_entries):
    artwork = None
    for entry in value:
        if entry.get("_label") == "Artwork":
            value.remove(entry)
            artwork = True
    if artwork and linked_art["classified_as"][0].get("classified_as", [{}])[0].get("_label", "") == "Type of Work":
        schema_org_entries.append(format_jsonld_entry("artForm",
                                                      linked_art["classified_as"][0]["_label"]))


def set_creator(key, value, linked_art, schema_org_entries):
    creator = None
    if key == "carried_out_by" and linked_art[key][0]["type"] == "Person":
        creator = linked_art["carried_out_by"][0]["_label"]
    elif "carried_out_by" in value and linked_art[key]["carried_out_by"][0]["type"] == "Person":
        creator = linked_art[key]["carried_out_by"][0]["_label"]
    if creator:
        schema_org_entries.append(
            f'  "creator": [\n    {{\n    "@type": "Person",\n    "name": "{creator}"\n    }}\n  ]')


def set_names(linked_art, schema_org_entries):
    name = linked_art["_label"]
    alternate_name = ""
    if linked_art.get("shown_by", [{}])[0].get("type", "") == "HumanMadeObject":
        name = linked_art["shown_by"][0]["_label"]
    if linked_art.get("shows", [{}])[0].get("type") == "VisualItem":
        alternate_name = linked_art["shows"][0]["_label"]
    elif linked_art.get("identified_by", [{}])[0].get("type", "") == "Name":
        alternate_name = linked_art["identified_by"][0]["content"]
    schema_org_entries.append(format_jsonld_entry("name", name))
    if alternate_name and alternate_name != name:
        schema_org_entries.append(format_jsonld_entry("alternateName", alternate_name))


def set_dimensions(linked_art, schema_org_entries):
    if linked_art.get("dimension"):
        dimensions = linked_art["dimension"]
        for dimension_dict in dimensions:
            dimension_type = dimension_dict["classified_as"][0]["_label"].lower()
            dimension = str(dimension_dict["value"]) + " " + dimension_dict["unit"]["_label"]
            schema_org_entries.append(format_jsonld_entry(dimension_type, dimension))


def set_art_materials(linked_art, schema_org_entries):
    if linked_art.get("made_of"):
        for material in linked_art["made_of"]:
            if material["type"] == "Material":
                if material["_label"].lower() in ["canvas", "paper", "wood", "board"]:
                    schema_org_entries.append(format_jsonld_entry("artworkSurface", material["_label"]))
                else:
                    schema_org_entries.append(format_jsonld_entry("artMedium", material["_label"]))


def format_schema_org_content(type_to_map, content_blocks):
    type_map = {"VisualItem": "VisualArtwork",
                "HumanMadeObject": "VisualArtwork",
                "ManMadeObject": "VisualArtwork"}

    schema_org_template = """\
<script type="application/ld+json">
{{
"@context": "https://schema.org",
"@type": "{type}"{formatted_blocks}
}}"""
    formatted_blocks = ""
    for block in content_blocks:
        formatted_blocks += ",\n" + block

    return schema_org_template.format(type=type_map[type_to_map],
                                      formatted_blocks=formatted_blocks)


def argument_parser():
    parser = ArgumentParser()
    parser.add_argument("LINKED_ART_JSONLD")
    return parser.parse_args()


if __name__ == '__main__':
    args = argument_parser()
    MappingProcessor(args.LINKED_ART_JSON)
