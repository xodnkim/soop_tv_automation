from bs4 import BeautifulSoup
with open('esports_dom.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

btn = soup.find_all('button')[10]
p = btn.parent
print(f'Parent 1: name={p.name}, class={p.get("class")}')
p2 = p.parent
print(f'Parent 2: name={p2.name}, class={p2.get("class")}')
p3 = p2.parent
print(f'Parent 3: name={p3.name}, class={p3.get("class")}')
