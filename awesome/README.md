# Awesome Portal: Data Bridge

This is a bridge used to put data and metadata from the Urban Flows Observatory into the [Awesome web portal](https://ufportal.clients.builtonawesomeness.co.uk/) via its API (see [Awesome Portal API Docs](https://ufapidocs.clients.builtonawesomeness.co.uk/)).

# Usage

```bash
$ cd awesome
$ python . --help
```

# Glossary

The metadata used to describe the sensor readings on each system is defined by a collection of objects. There are loose mappings between the two metadata systems.

## Urban Flows Observatory

* Site
* Sensor
* Pair

## Awesome Portal

* Location
* Sensor
* Reading Category
* Reading Type