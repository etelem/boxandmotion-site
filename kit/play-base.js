  // Play of the game: Damian Lillard's sidestep three with 43 seconds left that put Portland up six.
  // An original illustration from written accounts; not traced from footage, not to scale.
  function scenePlay(L, g, defs) {
    const {W, H, M, fs, P} = L;
    const k = P ? 0.82 : 1;
    const floor = P ? H * 0.8 : H - M - 70;
    const hoopX = P ? W - M - 30 : W - M - 120;
    const shotX = hoopX - (P ? 500 : 600) * k, startX = shotX + 90 * k;
    const rimY = floor - 240 * k * 1.62, rimR = 34 * k;
    const glow = S('filter', {id: 'glow', x: '-50%', y: '-50%', width: '200%', height: '200%'}, defs);
    S('feGaussianBlur', {stdDeviation: 6, result: 'b'}, glow);
    const merge = S('feMerge', {}, glow); S('feMergeNode', {in: 'b'}, merge); S('feMergeNode', {in: 'SourceGraphic'}, merge);

    const kicker = T(g, M, L.top + 6, 'Play of the game', 'k', fs.k);
    const head = fitAll([T(g, M, L.top + fs.h * 1.1, 'Dame Time', 'd', fs.h)], P ? W - 2 * M : W * 0.42)[0];
    const sub = T(g, M, L.top + fs.h * 1.1 + fs.s * 1.5, P ? 'The dagger, 43 seconds left' : 'The dagger, with 43 seconds left', 'b m', fs.s);
    const board = S('g', {}, g);
    const bx = M, by = L.top + fs.h * 1.1 + fs.s * (P ? 3.4 : 3.6);
    S('rect', {x: bx, y: by, width: 330, height: 92, rx: 12, class: 'f-navy', opacity: 0.85}, board);
    S('rect', {x: bx, y: by, width: 330, height: 92, rx: 12, class: 's-hair', 'stroke-width': 2}, board);
    T(board, bx + 24, by + 38, 'Q4', 'b m', 24);
    const sUs = T(board, bx + 24, by + 78, 'Blazers +3', 'b w', 26);
    T(board, bx + 306, by + 30, 'Clock', 'b m', 18, 'end');
    const qClock = T(board, bx + 306, by + 76, '48.0', 'd', 46, 'end');

    const court = S('g', {class: 's-silver', 'stroke-width': 3, 'stroke-linecap': 'round'}, g);
    const lines = [
      S('line', {x1: M - 20, x2: W - M + 20, y1: floor, y2: floor}, court),
      S('line', {x1: hoopX - 330 * k, x2: hoopX - 330 * k, y1: floor - 6, y2: floor + 14}, court),
      S('line', {x1: hoopX + 46 * k, x2: hoopX + 46 * k, y1: rimY - 120 * k, y2: floor}, court),
      S('line', {x1: hoopX + 46 * k, x2: hoopX + 46 * k + 40, y1: floor, y2: floor}, court),
    ];
    lines.forEach((n) => { n.setAttribute('pathLength', 1); n.setAttribute('stroke-dasharray', 1); n.setAttribute('stroke-dashoffset', 1); });
    const tag = T(g, hoopX - 330 * k, floor + 56 * k + 10, '3-pt line', 'b m', fs.s * 0.8, 'middle');
    S('rect', {x: hoopX + 30 * k, y: rimY - 150 * k, width: 12 * k, height: 170 * k, rx: 3, class: 'f-silver'}, g);
    S('line', {x1: hoopX - rimR, x2: hoopX + 30 * k, y1: rimY, y2: rimY, class: 's-red', 'stroke-width': 6, 'stroke-linecap': 'round'}, g);
    const net = S('g', {class: 's-silver', 'stroke-width': 2, opacity: 0.8}, g);
    for (let i = 0; i <= 4; i += 1) {
      const top = hoopX - rimR + i * (rimR * 2 / 4), bottom = hoopX - rimR * 0.55 + i * (rimR * 1.1 / 4);
      S('line', {x1: top, y1: rimY, x2: bottom, y2: rimY + 48 * k}, net);
    }

    // Lillard's trait: Dame Time. A giant game clock counts down behind him and freezes on the make.
    const bigClock = T(g, P ? W / 2 : (M + hoopX) / 2 + 60, P ? floor - 520 * k : floor - 190, '48.0', 'd', P ? 230 : 300, 'middle');
    bigClock.style.opacity = 0;
    // the sidestep: a bracket measures the space it opens between him and his defender.
    const space = S('g', {}, g);
    const spaceLine = S('line', {class: 's-silver', 'stroke-width': 3, filter: 'url(#glow)'}, space);
    const capL = S('line', {class: 's-silver', 'stroke-width': 3}, space), capR = S('line', {class: 's-silver', 'stroke-width': 3}, space);
    const spaceTxt = T(space, 0, 0, 'Space', 'b w', fs.s, 'middle');
    const ghost = figure(g, 'opp', k, '0');
    ghost.g.style.opacity = 0;

    const defender = figure(g, 'phi', k);
    defender.g.setAttribute('opacity', 0.75);
    const shooter = figure(g, 'opp', k, '0');
    const ghosts = [0, 1, 2, 3, 4].map(() => S('circle', {r: 12 * k, class: 'f-ink', opacity: 0}, g));
    const ball = S('circle', {r: 13 * k, class: 'f-ink', filter: 'url(#glow)'}, g);
    const T_JAB = 3.6, T_STEP = 4.3, T_SET = 4.9, T_JUMP = 5.2, T_REL = 5.9, T_MAKE = 10;
    const rel = [shotX + 30 * k, floor + (-306 - 54) * k];
    const peak = P ? 280 : 220;
    const arcAt = (u) => [lerp(rel[0], hoopX, u), lerp(rel[1], rimY - 6, u) - 4 * peak * u * (1 - u)];
    const trailPts = Array.from({length: 61}, (_, i) => arcAt(i / 60));
    const trail = S('path', {d: 'M' + trailPts.map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join('L'), class: 's-silver', 'stroke-width': 4, 'stroke-dasharray': '0 1', pathLength: 1, opacity: 0.85, filter: 'url(#glow)'}, g);
    const flash = S('circle', {cx: hoopX, cy: rimY, r: 0, class: 's-ink', 'stroke-width': 4, opacity: 0}, g);
    const plus = T(g, hoopX - rimR, rimY - 70 * k, '+3', 'd w', 72, 'end');
    const caption = S('g', {}, g);
    const capY = P ? floor + 150 : L.top + fs.h * 1.1 + fs.s * 1.5;
    if (P) {
      T(caption, M, capY, 'Blazers by 6, 43 seconds left.', 'b w', fs.b);
      T(caption, M, capY + fs.s * 1.5, 'The Lakers couldn’t recover.', 'b m', fs.s);
    } else {
      T(caption, M, capY + fs.s * 1.6, 'Blazers by 6 with 43 seconds left. The Lakers couldn’t recover.', 'b w', fs.b);
    }
    const slowmo = T(g, P ? W - M : W / 2, P ? L.top + 6 : floor + 56 * k + 10, 'Slow motion', 'k', fs.k, P ? 'end' : 'middle');

    // shooter position over time: probe, jab in, then hop back
    const xAt = (lt) => {
      if (lt < T_JAB) return startX + Math.sin(Math.max(0, lt - 1.2) * 2.4) * 10 * k;
      if (lt < T_STEP) return startX + 30 * k * prog(lt, T_JAB, 0.4);
      return lerp(startX + 30 * k, shotX, prog(lt, T_STEP, 0.45));
    };
    const defX = (lt) => lerp(startX + 150 * k, startX + 120 * k, prog(lt, T_JAB, 0.4)) + (lt > T_STEP + 0.3 ? -70 * k * prog(lt, T_STEP + 0.3, 0.9) : 0);

    return (lt) => {
      lines.forEach((n, i) => n.setAttribute('stroke-dashoffset', (1 - prog(lt, 0.1 + i * 0.12, 0.9)).toFixed(3)));
      [kicker, head, sub].forEach((n, i) => show(n, prog(lt, 0.2 + i * 0.15, 0.6), 18));
      show(board, prog(lt, 0.6, 0.6), 14);
      tag.style.opacity = prog(lt, 1, 0.6) * (1 - prog(lt, 9.5, 0.6));
      const made = lt >= T_MAKE;
      sUs.textContent = made ? 'Blazers +6' : 'Blazers +3';
      // clock: real time until the release, then slow motion, frozen at 42.8 on the make
      const clk = lt < T_REL ? 48 - (lt / T_REL) * 4.6 : lt < T_MAKE ? 43.4 - 0.6 * clamp((lt - T_REL) / (T_MAKE - T_REL)) : 42.8;
      qClock.textContent = clk.toFixed(1);
      bigClock.textContent = clk.toFixed(1);
      bigClock.style.opacity = (0.13 * prog(lt, 1, 0.8) + (made ? 0.25 * Math.exp(-(lt - T_MAKE) * 1.5) : 0)) * (1 - prog(lt, 13.6, 0.8));

      const sx = xAt(lt);
      let pose, lift = 0;
      if (lt < T_STEP) pose = lt < T_JAB ? POSES.dribble : mixPose(POSES.dribble, POSES.set, 0.35 * prog(lt, T_JAB, 0.3));
      else if (lt < T_SET) { pose = mixPose(POSES.dribble, POSES.set, prog(lt, T_STEP, 0.5)); lift = 22 * Math.sin(clamp((lt - T_STEP) / 0.45) * Math.PI); }
      else if (lt < T_JUMP) pose = POSES.set;
      else {
        const up = prog(lt, T_JUMP, 0.6), down = clamp((lt - 6.3) / 0.6);
        pose = lt < 6.3 ? mixPose(POSES.set, POSES.rise, up) : mixPose(POSES.rise, POSES.dribble, down);
        lift = lt < 6.3 ? 54 * up : 54 * (1 - down * down);
      }
      const at = shooter.draw(pose, sx, floor - lift * k, k, 1);
      shooter.g.style.opacity = prog(lt, 0.8, 0.6);
      // afterimage left where he stepped back from
      ghost.draw(POSES.dribble, startX + 30 * k, floor, k, 1);
      ghost.g.style.opacity = lt > T_STEP && lt < T_MAKE ? (0.28 * (1 - prog(lt, T_STEP + 1.2, 1.5))).toFixed(2) : 0;

      const dx = defX(lt);
      const dUp = prog(lt, 5.6, 0.6), dDown = clamp((lt - 6.4) / 0.6);
      const dPose = lt < 5.6 ? POSES.guard : lt < 6.4 ? mixPose(POSES.guard, POSES.contest, dUp) : mixPose(POSES.contest, POSES.guard, dDown);
      defender.draw(dPose, dx, floor - (lt < 6.4 ? 30 * dUp : 30 * (1 - dDown)) * k, k, -1);
      defender.g.style.opacity = 0.75 * prog(lt, 1, 0.6);

      // the space bracket opens with the step-back
      const sy = floor - 140 * k, a = sx + 34 * k, b = dx - 34 * k;
      const showSpace = lt > T_STEP + 0.2 && lt < T_REL + 0.6 && b > a;
      spaceLine.setAttribute('x1', a.toFixed(1)); spaceLine.setAttribute('x2', b.toFixed(1)); spaceLine.setAttribute('y1', sy.toFixed(1)); spaceLine.setAttribute('y2', sy.toFixed(1));
      capL.setAttribute('x1', a.toFixed(1)); capL.setAttribute('x2', a.toFixed(1)); capL.setAttribute('y1', (sy - 10).toFixed(1)); capL.setAttribute('y2', (sy + 10).toFixed(1));
      capR.setAttribute('x1', b.toFixed(1)); capR.setAttribute('x2', b.toFixed(1)); capR.setAttribute('y1', (sy - 10).toFixed(1)); capR.setAttribute('y2', (sy + 10).toFixed(1));
      spaceTxt.setAttribute('x', ((a + b) / 2).toFixed(1)); spaceTxt.setAttribute('y', (sy - 18).toFixed(1));
      space.style.opacity = showSpace ? Math.min(prog(lt, T_STEP + 0.2, 0.3), 1 - prog(lt, T_REL + 0.2, 0.4)) : 0;

      let bxp, byp;
      if (lt < T_SET) {
        const [hx, hy] = at('rh'), ph = Math.max(0, (lt - 1.2) / 0.42) % 1, f = ph < 0.5 ? ph * 2 : (1 - ph) * 2;
        bxp = hx + 6 * k; byp = lerp(hy, floor - 13 * k, f * f * (3 - 2 * f));
      } else if (lt < T_REL) {
        const [ax, ay] = at('lh'), [cx, cy] = at('rh');
        bxp = (ax + cx) / 2 + 4 * k; byp = (ay + cy) / 2 - 16 * k;
      } else if (lt < T_MAKE) {
        const v = clamp((lt - T_REL) / (T_MAKE - T_REL)), u = v < 0.5 ? 2 * v * v : 1 - Math.pow(-2 * v + 2, 2) / 2;
        [bxp, byp] = arcAt(u);
        ghosts.forEach((n, i) => {
          const [gx2, gy2] = arcAt(Math.max(0, u - (i + 1) * 0.025));
          n.setAttribute('cx', gx2.toFixed(1)); n.setAttribute('cy', gy2.toFixed(1)); n.setAttribute('opacity', (0.3 - i * 0.055).toFixed(2));
        });
        trail.setAttribute('stroke-dasharray', `${u.toFixed(3)} 1`);
      } else {
        const d = clamp((lt - T_MAKE) / 0.7);
        bxp = hoopX - 4; byp = lerp(rimY - 6, floor - 13 * k, d * d);
        if (d >= 1) { const bb = Math.abs(Math.sin((lt - T_MAKE - 0.7) * 7)) * Math.exp(-(lt - T_MAKE - 0.7) * 2.2); byp = floor - 13 * k - 80 * k * bb; }
        ghosts.forEach((n) => n.setAttribute('opacity', 0));
        trail.setAttribute('stroke-dasharray', '1 1');
      }
      if (lt < T_REL) { ghosts.forEach((n) => n.setAttribute('opacity', 0)); trail.setAttribute('stroke-dasharray', '0 1'); }
      ball.setAttribute('cx', bxp.toFixed(1)); ball.setAttribute('cy', byp.toFixed(1));
      ball.style.opacity = prog(lt, 0.8, 0.6);
      trail.style.opacity = 0.85 * (1 - prog(lt, 12.5, 1));
      slowmo.style.opacity = lt > T_REL + 0.3 && lt < T_MAKE ? 0.5 + 0.5 * Math.sin((lt - T_REL) * 6) : 0;

      const snap = made ? Math.exp(-(lt - T_MAKE) * 5) * Math.sin((lt - T_MAKE) * 22) : 0;
      net.setAttribute('transform', `translate(0 ${(rimY * -0.18 * snap).toFixed(1)}) scale(1 ${(1 + 0.18 * snap).toFixed(3)})`);
      const f = made ? clamp((lt - T_MAKE) / 0.8) : 0;
      flash.setAttribute('r', (rimR + 160 * f).toFixed(1)); flash.setAttribute('opacity', made ? (1 - f).toFixed(2) : 0);
      show(plus, made ? prog(lt, T_MAKE, 0.4) : 0, 20);
      show(caption, prog(lt, T_MAKE + 0.8, 0.6), 18);
      if (!P) sub.style.opacity = 1 - prog(lt, T_MAKE + 0.4, 0.4);
    };
  }

