"""Phase 4 independent reader: the raw Proteus IPC-D-356A file (own parser) and the KiCad kicadxml netlist
(kicad-cli export). No p2k code. Used by reading.py; `python3 ind.py REF | REF-PIN | NET` prints pins / nets."""
import os, re, subprocess, sys, tempfile, collections
import xml.etree.ElementTree as ET
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/"
def ipc():
    names={}; pins=collections.defaultdict(list); recs=[]
    for l in open(R+"source/cadcam/fpga_boardv2.5 - CADCAM Netlist.IPC", encoding="latin-1"):
        if l.startswith("P  NNAME"):
            k,v=l[3:].split(None,1); names[k]=v.strip(); continue
        if l[:3] in ("317","327"):
            net=l[3:17].strip(); net=names.get(net,net)
            ref=l[20:26].strip(); pin=l[27:31].strip()
            m=re.search(r"(?:D(\d{4})([PU]))?A(\d\d)X([+-]\d+)Y([+-]\d+)X(\d{4})(?:Y(\d{4}))?",l[31:])
            recs.append(dict(op=l[:3],net=net,ref=ref,pin=pin,drill=int(m[1] or 0)/1000,acc=m[3],x=int(m[4])/1000,y=int(m[5])/1000,w=int(m[6])/1000,h=int(m[7] or m[6])/1000))
            if ref and ref!="-": pins[(ref,pin)].append(net)
    return names,pins,recs
def kicad():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "net.xml")
        subprocess.run([R + "tools/p2k/bin/kicad-cli", "sch", "export", "netlist", "--format", "kicadxml", "-o", out,
                        R + "kicad/tube_control_card.kicad_sch"], check=True, capture_output=True)
        root = ET.parse(out).getroot()
    pn={}; 
    for n in root.iter("net"):
        for nd in n.findall("node"): pn[(nd.get("ref"),nd.get("pin"))]=(n.get("name"),nd.get("pinfunction"),nd.get("pintype"))
    comps={c.get("ref"):(c.findtext("value"),c.findtext("footprint"),c.find("sheetpath").get("names")) for c in root.iter("comp")}
    return pn,comps
if __name__=="__main__":
    names,pins,recs=ipc(); pn,comps=kicad()
    for a in sys.argv[1:]:
        if "-" in a and (a.split("-",1)[0],a.split("-",1)[1]) in pins:
            ref,pin=a.split("-",1); print(f"{a:10s} IPC {pins[(ref,pin)]}  KiCad {pn.get((ref,pin))}")
        elif a in comps:
            print(a, comps[a])
            for (r,p) in sorted(pins, key=lambda k:(k[0], [int(t) if t.isdigit() else t for t in re.split(r'(\d+)',k[1])] )):
                if r==a: print(f"  {p:5s} IPC {','.join(pins[(r,p)]):28s} KiCad {pn.get((r,p))}")
        else:
            print("net",a,":",sorted(f"{r}-{p}" for (r,p),ns in pins.items() if a in ns))
