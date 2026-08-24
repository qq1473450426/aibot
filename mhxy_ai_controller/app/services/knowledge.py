from pathlib import Path
class KnowledgeService:
    def __init__(self,root='knowledge/xyq-skills'):self.root=Path(root)
    def available(self):return self.root.exists()
    def search(self,q,max_files=5):
        if not self.available():return []
        out=[]
        for p in self.root.rglob('*.md'):
            t=p.read_text(encoding='utf-8',errors='ignore')
            if q.lower() in t.lower():out.append({'file':str(p),'snippet':t[:1000]})
            if len(out)>=max_files:break
        return out
