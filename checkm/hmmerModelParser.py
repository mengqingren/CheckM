###############################################################################
#
# hmmerModelParser.py - parse a HMMER model file
#
###############################################################################
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program. If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

class HmmModelError(Exception):
    pass

class HmmModel(object):
    """Store HMM model parameters."""
    def __init__(self, keys):
        setattr(self, 'isGatheringThreshold', False)
        setattr(self, 'isTrustedCutoff', False)
        setattr(self, 'isNoiseCutoff', False)
        
        if 'acc' not in keys:
            setattr(self, 'acc', keys['name'])
        
        for key, value in keys.items():
            setattr(self, key, value)
            
            if key == 'ga':
                setattr(self, 'isGatheringThreshold', True)
            elif key == 'tc':
                setattr(self, 'isTrustedCutoff', True)
            elif key == 'nc':
                setattr(self, 'isNoiseCutoff', True)
                
        

class HmmModelParser(object):
    """Parse HMM model file."""
    def __init__(self, hmmFile):
        self.hmmFile = open(hmmFile)

    def parse(self):
        fields = []
        headerKeys = dict()
        for line in self.hmmFile:
            if line.startswith("HMMER"):
                headerKeys['format'] = line.rstrip()
            elif line.startswith("HMM"):
                # beginning of the hmm model; iterate through till end of model
                for line in self.hmmFile:
                    if line.startswith("//"):
                        yield HmmModel(headerKeys)
                        break
            else:
                # header sections
                fields = line.rstrip().split(None, 1)
                if len(fields) != 2:
                    raise HmmModelError
                else:
                    # transform some data based on some of the header tags
                    if fields[0] == "LENG" or fields[0] == "NSEQ" or fields[0] == "CKSUM":
                        headerKeys[fields[0].lower()] = int(fields[1])
                    elif fields[0] == "RF" or fields[0] == "CS" or fields[0] == "MAP":
                        if fields[1].lower() == "no":
                            headerKeys[fields[0].lower()] = False
                        else:
                            headerKeys[fields[0].lower()] = True
                    elif fields[0] == "EFFN":
                        headerKeys[fields[0].lower()] = float(fields[1])
                    elif fields[0] == "GA" or fields[0] == "TC" or fields[0] == "NC":
                        params = fields[1].split()
                        if len(params) != 2:
                            raise HmmModelError
                        headerKeys[fields[0].lower()] = (float(params[0].replace(';','')), float(params[1].replace(';','')))
                    elif fields[0] == "STATS":
                        params = fields[1].split()
                        if params[0] != "LOCAL":
                            raise HmmModelError
                        if params[1] == "MSV" or params[1] == "VITERBI" or params[1] == "FORWARD":
                            headerKeys[(fields[0]+"_"+params[0]+"_"+params[1]).lower()] = (float(params[2]), float(params[3]))
                        else:
                            print("'"+params[1]+"'")
                            raise HmmModelError
                    else:
                        headerKeys[fields[0].lower()] = fields[1]