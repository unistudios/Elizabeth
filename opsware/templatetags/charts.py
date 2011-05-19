from django import template

import random

register = template.Library()

# Used to define the header part necessary to use FUSIONCharts
def ChartHeader(context):
    return {
        'MEDIA_URL':context['MEDIA_URL'],
    }
    
def ChartColor(category):
    colors = {'No Status' :"2F60E9",
              'Error'     :"D20808",
              'On-Hold'   :"F0F325",
              'Installed' :"1ECD15"
            }
    try:
        return colors[category]
    except:
        return category

def do_chart(parser, token):
    try:
        tag_name, type, width, height, url = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires five arguments: type, width, height, div, url" % token.contents.split()[0]

    return ChartNode(type, width, height, url)
    
class ChartNode(template.Node):
    def __init__(self, type, width, height, url):
        self.type = type.lower()
        self.width = width
        self.height = height
        self.url = url
        
    def render(self, context):
        murl = context['MEDIA_URL']
        
        randDIV = str(random.randint(1,10000) )
        
        if self.type == "pie3d":
            chartswf = "FCF_Pie3D.swf"
        elif self.type.lower() == "column3d":
            chartswf = "FCF_Column3D.swf"
        elif self.type.lower() == "mscolumn2d":
            chartswf = "FCF_MSColumn2D.swf"
        elif self.type.lower() == "mscolumn3d":
            chartswf = "FCF_MSColumn3D.swf"
        elif self.type.lower() == "mscolumn2dline":
            chartswf = "FCF_MSColumn2DLineDY.swf"
        elif self.type.lower() == "stackedcolumn2d":
            chartswf = "FCF_StackedColumn2D.swf"
        else:
            chartswf = "FCF_Column3D.swf"
        
        htmlstring =  '<! %s %s %s %s >\n' % (self.type, self.width, self.height, self.url)
        htmlstring += '<div id="%s" align="center"></div>' % (randDIV)
        htmlstring += '<script type="text/javascript">\n'
        htmlstring += '    var chart%s = new FusionCharts("%s/charts/%s", "ChartId", "%s", "%s");\n' % (randDIV, murl, chartswf, self.width, self.height)
        htmlstring += '    chart%s.setDataURL(%s);\n' % (randDIV, self.url)
        htmlstring += '    chart%s.render("%s");\n' % (randDIV, randDIV)
        htmlstring += '</script>\n'
        return htmlstring
 
   
register.inclusion_tag('tag_chartsheader.html', takes_context=True)(ChartHeader)
register.simple_tag(ChartColor)
register.tag('Chart', do_chart)
