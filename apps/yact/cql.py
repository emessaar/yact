#cql.py

from pyparsing import Word, delimitedList, Optional, \
    Group, alphanums, nums, alphas, ParseException, Forward, oneOf, quotedString, \
    ZeroOrMore, CaselessKeyword, CaselessLiteral, Combine, printables, OneOrMore

def printp(p):
    for k,v in p.items():
        print k, v

# define SQL tokens
cqlStmt = Forward()
SELECT = CaselessKeyword("select")
FROM = CaselessKeyword("from")
WHERE = CaselessKeyword("where")
CHART_FOR = CaselessKeyword("chart for")
SLICE_BY = CaselessKeyword("slice by")
TREND_BY = CaselessKeyword("trend by")

ident = Word( alphas, alphanums + "_$" )
function = Word(alphas)
ident2 = Word( alphas, alphanums + "_$" ) + Optional("|" + function)
identList = Group(delimitedList(ident, delim=','))
identList2 = Group(delimitedList(ident2, delim=','))
#chartname = Group(delimitedList(Word(alphas), delim=' '))
chartname = OneOrMore(~CHART_FOR + Word(alphas))

whereExpression = Forward()
AND = CaselessKeyword("and")
OR = CaselessKeyword("or")
IN = CaselessKeyword("in")
OF = CaselessKeyword("of")

E = CaselessLiteral("E")
arithSign = Word("+-",exact=1)
realNum = Combine( Optional(arithSign) + ( Word( nums ) + "." + Optional( Word(nums) )  |
                                                         ( "." + Word(nums) ) ) +
            Optional( E + Optional(arithSign) + Word(nums) ) )
intNum = Combine( Optional(arithSign) + Word( nums ) +
            Optional( E + Optional("+") + Word(nums) ) )

columnRVal = intNum | realNum | quotedString | ident

whereCondition = Group(
    ( ident + oneOf("= != < > >= <=") + columnRVal ) |
    ( ident + IN + "(" + delimitedList( columnRVal ) + ")" ) |
    ( "(" + whereExpression + ")" )
    )
whereExpression << whereCondition + ZeroOrMore( ( AND | OR ) + whereExpression )

# line chart for rev [per col1] by col2[, col3] [trend by col4] [where col5='aa' [and col6 > 5]]
# define the grammar
cqlStmt <<= (chartname("chart_name") + CHART_FOR + ident("chart_val")
                + (SLICE_BY + identList("sliceby"))
                + Optional(TREND_BY + ident("trendby"))
                + Optional(Group(WHERE + whereExpression), "")("filter")
            )
cqlStmt2 = Forward()
cqlStmt2 <<= (chartname("chart_name") + CHART_FOR + ident("chart_val")
                + (SLICE_BY + identList("sliceby"))
                + Optional(TREND_BY + ident("trendby"))
                + Optional(Group(WHERE + OneOrMore(Word(printables))), "")("filter")
            )

cqlStmt3 = Forward()
cqlStmt3 <<= (chartname("chart_name") + CHART_FOR + Optional(function("agg_fn") + OF) + ident("chart_val")
                + (SLICE_BY + identList("sliceby"))
                + Optional(TREND_BY + ident("trendby"))
                + Optional(Group(WHERE + OneOrMore(Word(printables))), "")("filter")
            )
