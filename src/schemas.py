from marshmallow import Schema, fields

from utils import DateFormat


class PricingSchema(Schema):
    type = fields.Str(dump_only=True, attribute='type_name')
    base_fare = fields.Decimal(dump_only=True)
    taxes = fields.Decimal(dump_only=True)
    total_amount = fields.Decimal(dump_only=True)


class FlightSchema(Schema):
    carrier_id = fields.Str(dump_only=True)
    carrier = fields.Str(dump_only=True, attribute='carrier_name')
    number = fields.Int(dump_only=True)
    source = fields.Str(dump_only=True, attribute='source_code')
    destination = fields.Str(dump_only=True, attribute='destination_code')
    departure_timestamp = fields.DateTime(
        dump_only=True, format=DateFormat.TIMESTAMP.value)
    arrival_timestamp = fields.DateTime(
        dump_only=True, format=DateFormat.TIMESTAMP.value)
    trip_class = fields.Str(dump_only=True)
    number_of_stops = fields.Int(dump_only=True)
    fare_basis = fields.Str(dump_only=True)
    warning_text = fields.Str(dump_only=True)
    ticket_type = fields.Str(dump_only=True)


class FlightsSchema(Schema):
    onward = fields.Nested(FlightSchema, dump_only=True, many=True)
    returned = fields.Nested(FlightSchema, dump_only=True, many=True)


class ProposalSchema(Schema):
    uuid = fields.Str(dump_only=True)
    flights = fields.Nested(FlightsSchema, dump_only=True)
    pricing = fields.Nested(PricingSchema, dump_only=True, many=True)
