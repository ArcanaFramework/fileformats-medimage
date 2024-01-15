from . import MaterialAnatomicalEntity


class AnatomicalStructure(MaterialAnatomicalEntity):
    pass


class CardinalOrganPart(AnatomicalStructure):
    pass


class OrganRegion(CardinalOrganPart):
    pass


class OrganSegment(OrganRegion):
    pass


class SegmentOfNeuraxis(OrganRegion):
    pass


class Brain(SegmentOfNeuraxis):
    pass


class SpinalCord(SegmentOfNeuraxis):
    pass
