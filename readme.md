![](https://github.com/courupteddata/StringBooleanExpression/workflows/Greet%20Everyone/badge.svg)

# String Boolean Expression
Ever wanted a maybe safe way to resolve or take in a boolean expression from the user or a configuration.

The input of:
S$employee_name==BoB||(F$salary<<20.5||F&salary>=100)
Is resolved to handle check if employees name equals BoB or the salary is in the range

## Comparison Map
|Input  	|Resolved comparison  	|
|---	|---	|
|==  	|equals  	|
|!=  	|not equal  	|
|\>>  	|greater than  	|
|<<  	|less than  	|
|>=  	|greater than or equal  	|
|<=  	|less than or equal  	|

## Type Map
|Input  	|Resolved type  	|
|---	|---	|
|S  	|string  	|
|I  	|integer  	|
|F  	|float  	|

## Operator Map
|Input  	|Resolved type  	|
|---	|---	|
|&#124;&#124;  	|or  	|
|&& 	|and  	|
|( 	|open grouping  	|
|) 	|close grouping  	|

## Default reserved keyword map
|Keyword  	|Resolved value  	|
|---	|---	|
|EMPTY_STRING  	|  	|


# Disclaimer
A best effort was done to restrict possible malicious input and if it is found then a ValueError is raised that needs to be caught.
