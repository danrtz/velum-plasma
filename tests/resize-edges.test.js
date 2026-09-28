// Run: deno test --allow-read tests/resize-edges.test.js
const src = Deno.readTextFileSync(new URL('../shell/kde/tiling/package/contents/code/engine.js', import.meta.url));
const { createEngine } = new Function(src + '\nreturn { createEngine };')();
const equal = (a, b) => {
    if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(JSON.stringify({ actual: a, expected: b }));
};
for (const side of ['right', 'left', 'down', 'up']) {
    for (const gaps of [0, 2]) {
        Deno.test(`nested ${side} resize keeps opposite edge fixed (gaps ${gaps})`, () => {
            const e = createEngine({ gapsIn: gaps, gapsOut: 4, preserveSplit: true });
            e.setArea('s', { x: 127, y: 48, width: 1800, height: 1200 });
            e.add('a', 's');
            e.add('b', 's', { target: 'a', side });
            e.add('c', 's', { target: 'a', side });
            const original = e.layout('s').windows;
            let before = original.c;
            for (const delta of [80, -30, -50, 65, -65]) {
                const after = { ...before };
                if (side === 'right') after.width += delta;
                if (side === 'left') { after.x += delta; after.width -= delta; }
                if (side === 'down') after.height += delta;
                if (side === 'up') { after.y += delta; after.height -= delta; }
                e.resizeByRects('c', before, after);
                const layout = e.layout('s').windows;
                equal(layout.c, after);
                equal(layout.a, original.a); // Window beyond the untouched edge.
                before = layout.c;
            }
            equal(e.layout('s').windows, original);
        });
    }
}
Deno.test('nested corner resize preserves both untouched edges', () => {
    const e = createEngine({ gapsIn: 2, gapsOut: 4, preserveSplit: true });
    e.setArea('s', { x: 0, y: 48, width: 1800, height: 1200 });
    e.add('a', 's');
    e.add('b', 's', { target: 'a', side: 'right' });
    e.add('c', 's', { target: 'a', side: 'right' });
    e.add('d', 's', { target: 'c', side: 'down' });
    e.add('e', 's', { target: 'c', side: 'down' });
    const before = e.layout('s').windows.e;
    const after = { ...before, width: before.width + 90, height: before.height + 50 };
    e.resizeByRects('e', before, after);
    equal(e.layout('s').windows.e, after);
});
