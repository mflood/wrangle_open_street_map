# Types of data auditing
> These are some notes I took on auditing data, in general

## Auditing Validity

    Figuring out the constraints of a field and making sure data adheres to those constraints
        e.g. are all "shops" and "amenities" valid choices?

    Ensure Phone Numbers are the correct pattern
    Ensure Street Names are stanardized
    Ensure zip codes are 5 digits


Cleaning Problematic Data

## Auditing Accuracy (requires gold standard data)
    for example: Compare country codes against ISO data


Problems
    Some countries are arrays

Regex Fixes - auto correct generally

## Auditing Completeness
    You don't know what you don't know
    Depends on the data and the resources you have access to
    missing records...
    Requires reference data to check for completeness


## Auditing Consistency

    same customer - two different addresses
    which data source do you trust the most?
    which data is more recent?
    which collection method is more reliable?
    copy the dasta form the record you trust the most
    
## Auditing Uniformity
    All values in a field using same units of measurement
    is it the right type of data (int vs float vs string)
    is it within min / max limits (check it's range)

    degrees / min / sec vs 40.123 for latitute

    Scalar Fields
    Array Fields


