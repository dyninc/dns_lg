# Provides a wrapper around a DNS library for use by the Dyn_lg module

#ldnsx is a wrapper around python-ldns, which is a wrapper around the C libldns1
#ldnsx is shipped with the source code for python-ldns
#jyoung modified ldnsx.py to get at all the info we need....
import ldnsx 

import string

#TODO need to make sure we get TXT RR for the 'ANY" query
#TODO should we include the question section in the output?
#TODO make sure JSON names match https://github.com/bortzmeyer/dns-lg/blob/master/JSON.txt
def query(domain, qtype, qclass, server, flags):
  """Run a query and return results."""

  if len(server) == 0:
    resolver = ldnsx.resolver()
  else:
    resolver = ldnsx.resolver(str(server))

  myDict = dict()
  qrySect = dict()
  queSect = dict()
  ansList = []
  autList = []
  addList = []

  #FIXME
  qrySect['Versions'] = "Dyn DNS Looking Glass 1.0.0"
#  qrySect['Description'] = ""
  #FIXME

  try:
    #configure the resolver
    #flags are the same options used for drill -o on the command line
    pkt = resolver.query(str(domain), str(qtype), str(qclass), flags, 1)

    if not pkt is None:
      for rr in pkt.question():
        queSect['Qname']  = rr.owner()
        queSect['Qtype']  = rr.rr_type()
        queSect['Qclass'] = rr.rr_class()
      for rr in pkt.additional():
        addList.append(decode_rr(rr))
      for rr in pkt.authority():
        autList.append(decode_rr(rr))
      for rr in pkt.answer():
        ansList.append(decode_rr(rr))
      qrySect['ServerIP'] = pkt.answer_from()
      qrySect['Duration'] = pkt.query_time()
      myDict['ReturnCode'] = pkt.rcode()
  except IOError, e:
    if not pkt is None:
      myDict['ReturnCode'] = pkt.rcode()
    else:
      myDict['ReturnCode'] = "TIMEOUT"
  finally:
    qrySect['Server'] = server.strip(".")
    myDict['AnswerSection'] = ansList
    myDict['AuthoritySection'] = autList
    myDict['AdditionalSection'] = addList

    for f in flags:
      myDict[f] = "true"

    myDict['Query'] = qrySect
    myDict['QuestionSection'] = queSect
    
  return myDict

def decode_rr (rr):
  global _decode_actions

  rrDict = dict()
  rr_type = rr.rr_type()
  rrDict['Name']  = rr.owner()
  rrDict['TTL']   = str(rr.ttl())
  rrDict['Type']  = rr.rr_type()
  rrDict['Class'] = rr.rr_class()

  if rr_type in _decode_actions:
    rrDict = _decode_actions[rr_type](rr, rrDict)

  return rrDict

def decode_addr(rr, rrDict):
  rrDict['Address']             = rr.ip()
  return rrDict

def decode_ns(rr, rrDict):
  rrDict['Target']            = rr.name_server()
  return rrDict

def decode_cname(rr, rrDict):
  rrDict['Target']            = rr.cname()
  return rrDict

def decode_mx(rr, rrDict):
  rrDict['MailExchanger']     = rr.mx_exchange()
  rrDict['Preference']        = rr.mx_priority()
  return rrDict

def decode_txt(rr, rrDict):
  rrDict['Text']              = rr.txt_value().strip('"')
  return rrDict

def decode_ptr(rr, rrDict):
  rrDict['Target']            = "TBD   - PTR TARGET"
  return rrDict

def decode_soa(rr, rrDict):
  rrDict['MaintainerName']    = rr.soa_maintainer()
  rrDict['MasterServerName']  = rr.soa_master()
  rrDict['Serial']            = rr.soa_serial()
  rrDict['Refresh']           = rr.soa_refresh()
  rrDict['Retry']             = rr.soa_retry()
  rrDict['Expire']            = rr.soa_expire()
  rrDict['NegativeTtl']       = rr.soa_negative_ttl()
  return rrDict

def decode_dnskey(rr, rrDict):
  rrDict['Algorithm']         = "TBD   - DNSKEY ALGORITHM"
  rrDict['Length']            = "TBD   - DNSKEY LENGTH"
  rrDict['Flags']             = "TBD   - DNSKEY FLAGS"
  rrDict['Tag']               = "TBD   - DNSKEY TAG"
  return rrDict

def decode_ds_dlv(rr, rrDict):
#  elif (rr_type == "DS") or (rr_type == "DLV"):
  rrDict['DelegationKey']     = "TBD   - DS/DLV DELEGATION KEY"
  rrDict['DigestType']        = "TBD   - DS/DLV DIGEST TYPE"
  return rrDict

def decode_nsec3(rr, rrDict):
  rrDict['Algorithm']         = "TBD   - NSEC3PARAM ALGORITHM "
  rrDict['Flags']             = "TBD   - NSEC3PARAM FLAGS"
  rrDict['Salt']              = "TBD   - NSEC3PARAM SALT"
  rrDict['Iterations']        = "TBD   - NSEC3PARAM ITERATIONS"
  return rrDict

def decode_sshfp(rr, rrDict):
  rrDict['Algorithm']         = "TBD   - SSHFP ALGORITHM"
  rrDict['DigestType']        = "TBD   - SSHFP DIGEST TYPE"
  rrDict['Fingerprint']       = "TBD   - SSHFP FINGERPRINT"
  return rrDict

def decode_naptr(rr, rrDict):
  rrDict['Flags']             = "TBD   - NAPTR FLAGS"
  rrDict['Order']             = "TBD   - NAPTR ORDER"
  rrDict['Services']          = "TBD   - NAPTR SERVICE"
  rrDict['Preference']        = "TBD   - NAPTR PREFERENCE"
  rrDict['Regexp']            = "TBD   - NAPTR REGEXP"
  rrDict['Replacement']       = "TBD   - NAPTR REPLACEMENT"
  return rrDict

def decode_srv(rr, rrDict):
  rrDict['Server']            = "TBD   - SRV SERVER"
  rrDict['Port']              = "TBD   - SRV PORT"
  rrDict['Priority']          = "TBD   - SRV PRIORITY"
  rrDict['Weight']            = "TBD   - SRV WEIGHT"
  return rrDict

def decode_loc(rr, rrDict):
  rrDict['Longitude']         = "TBD   - LOC LONG"
  rrDict['Latitude']          = "TBD   - LOC LAT"
  rrDict['Altitude']          = "TBD   - LOC ALT"
  return rrDict

_decode_actions = { 'A' : decode_addr,
                    'AAAA' : decode_addr,
                    'NS' : decode_ns,
                    'CNAME' : decode_cname,
                    'MX' : decode_mx,
                    'TXT' : decode_txt,
                    'SPF' : decode_txt,
                    'PTR' : decode_ptr,
                    'SOA' : decode_soa,
                    'DNSKEY' : decode_dnskey,
                    'DS' : decode_ds_dlv,
                    'DLV' : decode_ds_dlv,
                    'NSEC3PARAM' : decode_nsec3,
                    'SSHFP' : decode_sshfp,
                    'NAPTR' : decode_naptr,
                    'SRV' : decode_srv,
                    'LOC' : decode_loc }

