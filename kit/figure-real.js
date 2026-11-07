  // A player-proportioned silhouette: tapered limbs with muscle curves, a sleeveless jersey over the torso, knee-length
  // shorts, high-top sneakers and a head with a plain hair line. Height, arm length and build come from the player's
  // listed measurements (b.tall = height vs the 6'6" generic figure, b.ape = wingspan / height, b.mass = weight per inch
  // of height vs the generic figure). Drawn twice: a glowing outline layer under a solid fill layer. The face stays
  // featureless on purpose: the resemblance is build, number, colors and the moment, not a portrait.
  function figureReal(parent, team, k, number, b) {
    b = Object.assign({tall: 1, mass: 1, ape: 1}, b || {});
    const g = S('g', {'stroke-linecap': 'round', 'stroke-linejoin': 'round'}, parent);
    const outline = S('g', {class: `fig-o-${team}`}, g);
    if (team === 'phi') outline.setAttribute('filter', 'url(#glow)');
    const fill = S('g', {}, g);
    const PARTS = ['armB', 'legB', 'legF', 'shorts', 'torso', 'jersey', 'band', 'neck', 'armF', 'head', 'hair', 'shoes'];
    const CLS = {armB: 'fig-skin', legB: 'fig-skin', legF: 'fig-skin', shorts: `fig-kit-${team}`, torso: 'fig-skin', jersey: `fig-kit-${team}`, band: 'fig-band', neck: 'fig-skin', armF: 'fig-skin', head: 'fig-skin', hair: 'fig-hair', shoes: 'fig-shoe'};
    const OX = 7 * k;
    const o = {}, f = {};
    PARTS.forEach((p) => {
      if (p !== 'jersey' && p !== 'band') o[p] = S('path', {'stroke-width': OX.toFixed(1)}, outline);
      if (p === 'armF') {
        // the front arm crosses the jersey, so it gets its own thin edge to read as an arm, not a strap
        f.armEdge = S('path', {class: `fig-o-${team}`, 'stroke-width': (4 * k).toFixed(1)}, fill);
      }
      f[p] = S('path', {class: CLS[p], 'stroke-width': (p === 'band' ? 3 * k : p === 'jersey' || p === 'shorts' ? 2 * k : 0.5).toFixed(1)}, fill);
      if (p === 'jersey' && number != null) {
        f.num = S('text', {class: 'fig-num', 'text-anchor': 'middle'}, fill);
        f.num.textContent = number; f.num.style.fontSize = (30 * k).toFixed(1) + 'px';
      }
    });
    const F = (v) => v.toFixed(1);
    const add = (a, b2, s = 1) => [a[0] + b2[0] * s, a[1] + b2[1] * s];
    // a tapered capsule from A to B: width w1 at A, wm at the muscle belly (fraction t along), w2 at B
    const seg = (A, B, w1, wm, w2, t = 0.4, belly = 0) => {
      const dx = B[0] - A[0], dy = B[1] - A[1], L = Math.hypot(dx, dy) || 1, u = [dx / L, dy / L], n = [-u[1], u[0]];
      const m = add(A, u, L * t);
      const side = (s) => {
        const a = add(A, n, s * w1 / 2), e = add(B, n, s * w2 / 2), mm = add(m, n, s * (wm / 2 + (s > 0 ? belly : 0)));
        return [a, [2 * mm[0] - (a[0] + e[0]) / 2, 2 * mm[1] - (a[1] + e[1]) / 2], e];
      };
      const [a1, c1, b1] = side(1), [a2, c2, b2] = side(-1);
      const capB = w2 * 0.66, capA = w1 * 0.66;
      return `M${F(a1[0])} ${F(a1[1])}Q${F(c1[0])} ${F(c1[1])} ${F(b1[0])} ${F(b1[1])}`
        + `C${F(b1[0] + u[0] * capB)} ${F(b1[1] + u[1] * capB)} ${F(b2[0] + u[0] * capB)} ${F(b2[1] + u[1] * capB)} ${F(b2[0])} ${F(b2[1])}`
        + `Q${F(c2[0])} ${F(c2[1])} ${F(a2[0])} ${F(a2[1])}`
        + `C${F(a2[0] - u[0] * capA)} ${F(a2[1] - u[1] * capA)} ${F(a1[0] - u[0] * capA)} ${F(a1[1] - u[1] * capA)} ${F(a1[0])} ${F(a1[1])}Z`;
    };
    const poly = (pts) => 'M' + pts.map(([x, y]) => `${F(x)} ${F(y)}`).join('L') + 'Z';
    return {
      g,
      draw(pose, x, y, kk, dir) {
        const K = k * b.tall, W = k * b.mass;
        const P0 = (j) => [x + dir * pose[j][0] * K, y + pose[j][1] * K];
        const J = {};
        ['head', 'neck', 'hip', 'lk', 'lf', 'rk', 'rf'].forEach((j) => { J[j] = P0(j); });
        const N = J.neck, Hp = J.hip;
        let ax = N[0] - Hp[0], ay = N[1] - Hp[1]; const len = Math.hypot(ax, ay) || 1; ax /= len; ay /= len;
        const px = -ay, py = ax;
        const along = (pt, s, w, d) => [pt[0] + px * s * w * W + ax * d * K, pt[1] + py * s * w * W + ay * d * K];
        const shoulder = (side) => [N[0] + dir * side * 12 * W - ax * 8 * K, N[1] - ay * 8 * K];
        // arms grow from the shoulder by the wingspan ratio
        [['l', -1], ['r', 1]].forEach(([s, side]) => {
          const sh = shoulder(side), e = P0(s + 'e'), h = P0(s + 'h');
          const E = add(sh, [e[0] - sh[0], e[1] - sh[1]], b.ape);
          J[s + 'e'] = E; J[s + 'h'] = add(E, [h[0] - e[0], h[1] - e[1]], b.ape); J[s + 's'] = sh;
        });
        const arm = (s) => seg(J[s + 's'], J[s + 'e'], 15 * W, 16 * W, 11 * W, 0.3) + seg(J[s + 'e'], J[s + 'h'], 11 * W, 12 * W, 8 * W, 0.3);
        const ankle = (ft) => [ft[0] - dir * 2 * k, ft[1] - 16 * k];
        const leg = (s) => seg(Hp, J[s + 'k'], 25 * W, 27 * W, 15 * W, 0.35) + seg(J[s + 'k'], ankle(J[s + 'f']), 15 * W, 18 * W, 10 * W, 0.3);
        const shortsTo = (s) => [lerp(Hp[0], J[s + 'k'][0], 0.72), lerp(Hp[1], J[s + 'k'][1], 0.72)];
        const shorts = seg(add(Hp, [ax, ay], 6 * K), shortsTo('l'), 30 * W, 31 * W, 28 * W, 0.5) + seg(add(Hp, [ax, ay], 6 * K), shortsTo('r'), 30 * W, 31 * W, 28 * W, 0.5)
          + poly([along(Hp, 1, 18, 10), along(Hp, -1, 18, 10), along(Hp, -1, 17, -6), along(Hp, 1, 17, -6)]);
        // torso: broad at the shoulders, tapering to the waist; the jersey sits on it with narrow straps and open armholes
        const torso = poly([along(N, 1, 24, -6), along(N, 1, 23, -24), along(Hp, 1, 16, 26), along(Hp, 1, 16, 0), along(Hp, -1, 16, 0), along(Hp, -1, 16, 26), along(N, -1, 23, -24), along(N, -1, 24, -6)]);
        const jersey = poly([along(N, 1, 11, -2), along(N, 1, 14, -6), along(N, 1, 18, -30), along(Hp, 1, 17, 22), along(Hp, 1, 17, 6), along(Hp, -1, 17, 6), along(Hp, -1, 17, 22), along(N, -1, 18, -30), along(N, -1, 14, -6), along(N, -1, 11, -2), along(N, 0, 0, -12)]);
        const hd = J.head, rx = 14 * W * 1.02, ry = 17.5 * K / b.tall * Math.sqrt(b.tall);
        const neck = seg(add(N, [ax, ay], -4 * K), [lerp(N[0], hd[0], 0.65), lerp(N[1], hd[1], 0.65)], 13 * W, 12 * W, 12 * W, 0.5);
        const head = `M${F(hd[0] - rx)} ${F(hd[1])}A${F(rx)} ${F(ry)} 0 1 0 ${F(hd[0] + rx)} ${F(hd[1])}A${F(rx)} ${F(ry)} 0 1 0 ${F(hd[0] - rx)} ${F(hd[1])}Z`;
        // a plain, close-cropped hair cap: higher at the forehead, lower at the back
        const cap = []; for (let i = 0; i <= 16; i += 1) { const th = -Math.PI * 1.06 + (Math.PI * 0.86) * i / 16; cap.push([hd[0] + dir * (rx + 1.2 * k) * Math.cos(th), hd[1] + (ry + 1.2 * k) * Math.sin(th)]); }
        const hair = poly(cap.concat([[hd[0] + dir * rx * 0.35, hd[1] - ry * 0.45], [hd[0] - dir * rx * 0.3, hd[1] - ry * 0.2]]));
        const shoe = (ft) => poly([[ft[0] - dir * 7 * k, ft[1]], [ft[0] + dir * 21 * k, ft[1]], [ft[0] + dir * 20 * k, ft[1] - 8 * k], [ft[0] + dir * 7 * k, ft[1] - 12 * k], [ft[0] + dir * 5 * k, ft[1] - 21 * k], [ft[0] - dir * 7 * k, ft[1] - 21 * k]]);
        const crotch = add(Hp, [ax, ay], -8 * K), sl = shortsTo('l'), sr = shortsTo('r');
        const band = `M${F(along(Hp, 1, 17, 6)[0])} ${F(along(Hp, 1, 17, 6)[1])}L${F(along(Hp, -1, 17, 6)[0])} ${F(along(Hp, -1, 17, 6)[1])}M${F(crotch[0])} ${F(crotch[1])}L${F((sl[0] + sr[0]) / 2)} ${F((sl[1] + sr[1]) / 2)}`;
        const D2 = {band, armB: arm('l'), legB: leg('l'), legF: leg('r'), shorts, torso, jersey, neck, armF: arm('r'), head, hair, shoes: shoe(J.lf) + shoe(J.rf)};
        PARTS.forEach((p) => { f[p].setAttribute('d', D2[p]); if (o[p]) o[p].setAttribute('d', D2[p]); });
        f.armEdge.setAttribute('d', D2.armF);
        if (f.num) { const c = [lerp(N[0], Hp[0], 0.45), lerp(N[1], Hp[1], 0.45)]; f.num.setAttribute('x', F(c[0])); f.num.setAttribute('y', F(c[1] + 10 * k)); }
        return (j) => J[j];
      },
    };
  }
