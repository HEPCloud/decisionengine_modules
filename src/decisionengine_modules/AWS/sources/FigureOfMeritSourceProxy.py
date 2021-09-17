"""
Calculates price / preformance and figure of merit and
saves it into the output file acording to design document.

"""

from decisionengine.framework.modules import Source, SourceProxy

FigureOfMeritSourceProxy = SourceProxy.SourceProxy
Source.describe(FigureOfMeritSourceProxy)
