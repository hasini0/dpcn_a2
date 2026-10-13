"""DEMO ONLY: synthetic raw data in OpenAlex shape, to test the pipeline. NOT real publications."""
import json, os, random
random.seed(7)
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw_demo"); os.makedirs(D, exist_ok=True)
insts = [{"name": n, "id": f"I{i}", "display": d} for i, (n, d) in enumerate([
 ("SN Bose National Centre","S. N. Bose National Centre for Basic Sciences"),("Bose Institute Kolkata","Bose Institute"),
 ("SINP Kolkata","Saha Institute of Nuclear Physics"),("NCBS Bangalore","National Centre for Biological Sciences")],1)]
partners=["Indian Institute of Science","Indian Association for the Cultivation of Science","Indian Institute of Technology Bombay","Jadavpur University","Tata Institute of Fundamental Research","University of Calcutta","CSIR - National Chemical Laboratory","Homi Bhabha National Institute","Indian Statistical Institute","Indian Institute of Science Education and Research Pune"]
foreign=["CERN","MIT","University of Tokyo"]
fields=[("Physics and Astronomy","Condensed Matter Physics"),("Physics and Astronomy","Nuclear and High Energy Physics"),("Biochemistry, Genetics and Molecular Biology","Molecular Biology"),("Agricultural and Biological Sciences","Plant Science"),("Materials Science","Biomaterials"),("Chemistry","Physical and Theoretical Chemistry")]
journals=[("Physical Review B","0163-1829","journal"),("Physical Review D","1550-7998","journal"),("Journal of High Energy Physics","1029-8479","journal"),("eLife","2050-084X","journal"),("PLOS ONE","1932-6203","journal"),("Scientific Reports","2045-2322","journal"),("Journal of Physics Condensed Matter","0953-8984","journal"),("Nucleic Acids Research","0305-1048","journal"),("Physics Letters B","0370-2693","journal"),("Proc. Intl Conf on Machine Learning","","conference")]
faculty={i["id"]:[(f"A{i['id'][1:]}{k:03d}",f"Dr. {chr(65+k%26)}{chr(97+(k*3)%26)}{chr(97+(k*7)%26)}{chr(97+(k*5)%26)}an {chr(65+(k*11)%26)}.") for k in range(45)] for i in insts}
ext=[(f"X{k}",f"Ext Author {k}") for k in range(300)]
def inst_obj(n,c="IN",i=None): return {"id":f"https://openalex.org/{i or 'I9'+str(abs(hash(n))%999)}","display_name":n,"country_code":c}
works=[];authors={}
for i in insts:
    for aid,nm in faculty[i["id"]]: authors[aid]={"name":nm,"h":int(random.paretovariate(1.6)*5)%70,"works":50,"cites":900}
for n in range(1,1101):
    inst=random.choice(insts); y=random.randint(2016,2026)
    pool=faculty[inst["id"]]; na=random.choice([2,3,3,4,5,6,8])
    au=random.sample(pool,min(na,len(pool))); sh=[]
    if random.random()<.3:
        o=random.choice([x for x in insts if x is not inst]); au+=random.sample(faculty[o["id"]],2)
    ships=[]
    for aid,nm in au:
        io=[i2 for i2 in insts if (aid,nm) in faculty[i2["id"]]][0]
        ships.append({"author":{"id":f"https://openalex.org/{aid}","display_name":nm},"institutions":[{"id":f"https://openalex.org/{io['id']}","display_name":io["display"],"country_code":"IN"}]})
    for _ in range(random.choice([0,0,1,2,3])):
        e=random.choice(ext+[]);p=random.choice(partners+foreign)
        ships.append({"author":{"id":f"https://openalex.org/{e[0]}","display_name":e[1]},"institutions":[inst_obj(p,"IN" if p in partners else "XX")]})
    j=random.choices(journals,[10,8,8,5,6,6,6,4,6,1])[0]; f=random.choice(fields)
    works.append({"id":f"https://openalex.org/W{n}","doi":f"https://doi.org/10.9999/demo.{n}","title":f"[DEMO] Synthetic study {n} on {f[1].lower()}","publication_year":y,
      "type":"proceedings-article" if j[2]=="conference" else "article","primary_location":{"source":{"display_name":j[0],"issn_l":j[1] or None,"issn":[j[1]] if j[1] else [],"type":j[2]}},
      "cited_by_count":int(random.paretovariate(1.2)*2)-1 if y<2025 else random.randint(0,3),"authorships":ships,"referenced_works":[],"primary_topic":{"field":{"display_name":f[0]},"subfield":{"display_name":f[1]}}})
    works[-1]["cited_by_count"]=max(0,works[-1]["cited_by_count"])
refs={};citers={}
for w in works:
    k=int(w["id"].split("W")[1])
    older=[x for x in works if x["publication_year"]<w["publication_year"]]
    w["referenced_works"]=[x["id"] for x in random.sample(older,min(len(older),random.randint(0,4)))]
    for _ in range(random.randint(0,3)):
        r=f"R{k}_{_}"; w["referenced_works"].append(f"https://openalex.org/{r}")
        refs[r]={"doi":f"https://doi.org/10.8888/ref.{r}","year":2010+random.randint(0,6),"insts":[[random.choice(partners+foreign),"IN"]]}
        if refs[r]["insts"][0][0] in foreign: refs[r]["insts"][0][1]="XX"
    for _ in range(random.choice([0,1,2,3])):
        cid=f"C{k}_{_}"; p=random.choice(partners)
        citers[cid]={"doi":f"https://doi.org/10.7777/cit.{cid}","year":min(2026,w["publication_year"]+random.randint(0,3)),"insts":[[p,"IN"]],"refs":[w["id"].split("/")[-1]]}
json.dump(insts,open(D+"/institutions.json","w"));json.dump(works,open(D+"/works.json","w"));json.dump(authors,open(D+"/authors.json","w"));json.dump(refs,open(D+"/refs.json","w"));json.dump(citers,open(D+"/citers.json","w"))
print("demo written")
