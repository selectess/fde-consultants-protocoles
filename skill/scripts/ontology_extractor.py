#!/usr/bin/env python3
"""
Ontology Extractor
==================

Extracts a candidate ontology (objects, properties, links, actions)
from interview transcripts or notes — Palantir Foundry-style.

Usage:
    python ontology_extractor.py --input notes.md --output ontology.json
    python ontology_extractor.py --interactive

Output:
    JSON ontology spec + Mermaid ER diagram
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class ObjectType:
    """A real-world entity in the customer's domain."""
    name: str
    description: str
    properties: List[str] = field(default_factory=list)


@dataclass
class LinkType:
    """A relationship between object types."""
    name: str
    from_type: str
    to_type: str
    cardinality: str = "many-to-many"  # one-to-one, one-to-many, many-to-many


@dataclass
class ActionType:
    """An action that can be performed on an object type."""
    name: str
    target_type: str
    description: str
    side_effects: List[str] = field(default_factory=list)


@dataclass
class Ontology:
    objects: List[ObjectType] = field(default_factory=list)
    links: List[LinkType] = field(default_factory=list)
    actions: List[ActionType] = field(default_factory=list)


def heuristic_extract(text: str) -> Ontology:
    """
    Extract candidate ontology from text using heuristics.

    Look for:
    - Nouns that appear frequently (candidate objects)
    - Verbs describing actions
    - Possessives and "of" phrases (candidate properties)
    - "X has many Y" / "Y belongs to X" (candidate links)
    """
    text_lower = text.lower()

    # Heuristic object detection — broad coverage across SaaS, B2B, manufacturing, healthcare
    object_candidates = {
        # Generic / SaaS
        "customer": "A person or organization that buys products/services",
        "order": "A purchase transaction",
        "product": "An item or service offered",
        "user": "A person using the system",
        "project": "A unit of work",
        "ticket": "A support request",
        "employee": "A person employed by the organization",
        "invoice": "A bill for goods/services",
        "payment": "A monetary transaction",
        "subscription": "A recurring service agreement",
        "account": "A customer relationship record",
        "lead": "A potential customer",
        "campaign": "A marketing initiative",
        "asset": "A resource owned",
        "document": "A piece of content",
        "task": "A unit of work to be done",
        "event": "Something that happened",
        # Manufacturing / industrial
        "disc": "A manufactured part",
        "defect": "A quality issue on a part",
        "batch": "A production run",
        "line": "A production line",
        "machine": "Manufacturing equipment",
        "operator": "A person operating equipment",
        "inspection": "A quality check event",
        # Healthcare
        "patient": "A person receiving care",
        "appointment": "A scheduled encounter",
        "diagnosis": "A medical assessment",
        "prescription": "A medication order",
        # Logistics
        "shipment": "A package in transit",
        "warehouse": "A storage facility",
        "vehicle": "A transport unit",
        "route": "A delivery path",
        # Fintech
        "transaction": "A financial event",
        "loan": "A lending agreement",
        "claim": "An insurance claim",
    }

    detected_objects = []
    for obj_name, description in object_candidates.items():
        # Count occurrences
        count = len(re.findall(r'\b' + obj_name + r'\b', text_lower))
        if count >= 2:  # Threshold
            detected_objects.append(ObjectType(
                name=obj_name.capitalize(),
                description=description,
                properties=[],  # User adds manually
            ))

    # Heuristic link detection
    link_patterns = [
        (r'(\w+) (?:has|have) (?:many )?(\w+)s?', "one-to-many"),
        (r'(\w+) (?:belongs? to|is part of) (\w+)', "many-to-one"),
        (r'(\w+) (?:is assigned to|assigned to) (\w+)', "many-to-one"),
    ]

    detected_links = []
    obj_names = {o.name.lower() for o in detected_objects}

    for pattern, cardinality in link_patterns:
        for match in re.finditer(pattern, text_lower):
            from_obj = match.group(1).capitalize()
            to_obj = match.group(2).capitalize()
            # Strip trailing 's' for plural
            if to_obj.endswith('s') and to_obj[:-1].lower() in obj_names:
                to_obj = to_obj[:-1].capitalize()
            if from_obj.lower() in obj_names and to_obj.lower() in obj_names:
                link = LinkType(
                    name=f"{from_obj}Has{to_obj}",
                    from_type=from_obj,
                    to_type=to_obj,
                    cardinality=cardinality,
                )
                if link not in detected_links:
                    detected_links.append(link)

    # Heuristic action detection
    action_verbs = ["create", "update", "delete", "approve", "reject", "assign", "close", "open", "send", "receive"]
    detected_actions = []
    for verb in action_verbs:
        pattern = r'\b' + verb + r'\b\s+(?:a |an )?(\w+)'
        for match in re.finditer(pattern, text_lower):
            target = match.group(1).capitalize()
            if target.lower() in obj_names or target.lower().rstrip('s') in obj_names:
                action = ActionType(
                    name=verb.capitalize() + target,
                    target_type=target,
                    description=f"{verb.capitalize()} a {target.lower()}",
                )
                if action not in detected_actions:
                    detected_actions.append(action)

    return Ontology(
        objects=detected_objects,
        links=detected_links,
        actions=detected_actions,
    )


def to_mermaid(ontology: Ontology) -> str:
    """Render ontology as Mermaid ER diagram."""
    lines = ["```mermaid", "erDiagram"]

    # Objects with properties as attributes
    for obj in ontology.objects:
        obj_name = obj.name.upper()
        lines.append(f"    {obj_name} {{")
        for prop in obj.properties[:10]:  # Limit to 10 properties per object
            lines.append(f"        string {prop}")
        if not obj.properties:
            lines.append(f"        string id")
        lines.append("    }")

    # Links
    for link in ontology.links:
        from_name = link.from_type.upper()
        to_name = link.to_type.upper()
        # ER diagram cardinality
        card_map = {
            "one-to-one": "||--||",
            "one-to-many": "||--o{",
            "many-to-many": "}o--o{",
            "many-to-one": "}o--||",
        }
        symbol = card_map.get(link.cardinality, "}o--o{")
        lines.append(f"    {from_name} {symbol} {to_name} : {link.name}")

    lines.append("```")
    return "\n".join(lines)


def interactive_mode():
    """Build ontology interactively."""
    print("=" * 70)
    print("ONTOLOGY EXTRACTOR — Interactive")
    print("=" * 70)
    print()
    print("Define the core objects (entities) in your customer's domain.")
    print()

    ontology = Ontology()

    # Objects
    while True:
        print(f"\nObject #{len(ontology.objects) + 1}")
        name = input("Object name (e.g., Customer, Order, Product): ").strip()
        if not name:
            break
        description = input(f"Description of {name}: ").strip()

        obj = ObjectType(name=name.capitalize(), description=description)

        # Properties
        print(f"Properties of {name} (one per line, empty to stop):")
        while True:
            prop = input(f"  - {name} has property: ").strip()
            if not prop:
                break
            obj.properties.append(prop)

        ontology.objects.append(obj)

    # Links
    print("\n" + "=" * 70)
    print("LINKS (relationships between objects)")
    while True:
        print(f"\nLink #{len(ontology.links) + 1}")
        obj_names = [o.name for o in ontology.objects]
        for i, name in enumerate(obj_names):
            print(f"  {i+1}. {name}")

        from_idx = input(f"From object (1-{len(obj_names)}, empty to stop): ").strip()
        if not from_idx:
            break
        to_idx = input(f"To object (1-{len(obj_names)}): ").strip()
        cardinality = input("Cardinality (one-to-one / one-to-many / many-to-many) [many-to-many]: ").strip() or "many-to-many"

        ontology.links.append(LinkType(
            name=f"{obj_names[int(from_idx)-1]}Has{obj_names[int(to_idx)-1]}",
            from_type=obj_names[int(from_idx)-1],
            to_type=obj_names[int(to_idx)-1],
            cardinality=cardinality,
        ))

    # Actions
    print("\n" + "=" * 70)
    print("ACTIONS (operations on objects)")
    while True:
        print(f"\nAction #{len(ontology.actions) + 1}")
        name = input("Action name (e.g., CreateOrder, ApproveInvoice): ").strip()
        if not name:
            break
        target = input("Target object: ").strip()
        description = input(f"Description: ").strip()

        ontology.actions.append(ActionType(
            name=name,
            target_type=target,
            description=description,
        ))

    return ontology


def main():
    parser = argparse.ArgumentParser(description="Extract ontology from interview notes")
    parser.add_argument("--input", help="Input text file (interview notes)")
    parser.add_argument("--output", help="Output JSON file")
    parser.add_argument("--interactive", action="store_true")
    args = parser.parse_args()

    if args.interactive:
        ontology = interactive_mode()
    elif args.input:
        with open(args.input) as f:
            text = f.read()
        print(f"Extracting ontology from {args.input}...")
        ontology = heuristic_extract(text)
    else:
        parser.print_help()
        sys.exit(1)

    # Output
    print()
    print("=" * 70)
    print("EXTRACTED ONTOLOGY")
    print("=" * 70)
    print()
    print(f"Objects: {len(ontology.objects)}")
    for obj in ontology.objects:
        print(f"  - {obj.name}: {obj.description} ({len(obj.properties)} properties)")
    print()
    print(f"Links: {len(ontology.links)}")
    for link in ontology.links:
        print(f"  - {link.from_type} → {link.to_type} ({link.cardinality})")
    print()
    print(f"Actions: {len(ontology.actions)}")
    for action in ontology.actions:
        print(f"  - {action.name}: {action.description}")
    print()
    print("=" * 70)
    print("MERMAID ER DIAGRAM")
    print("=" * 70)
    print(to_mermaid(ontology))

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(asdict(ontology), f, indent=2, ensure_ascii=False)
        print(f"\nOntology saved to {args.output}")


if __name__ == "__main__":
    main()
