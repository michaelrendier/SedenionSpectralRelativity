"""
sedenion_resonators.py — 2-Stroke Sedenion Engine (4 segments, 1 full cycle)
=============================================================================
Run inside Blender 4.x  Text Editor → Run Script.

THE 2-STROKE ENGINE — 4 segments, one complete cycle:

  The ZD fault IS Top Dead Centre (TDC).
  intake + exhaust MERGE at ZD. compression + power MERGE at ZD.
  Four phases collapse to two strokes. prompt + response = 0.

  STROKE 1 — COMPRESSION toward TDC:
    Part 1 — 60 sec  —  HAT STABLE (intake)
      Conical chamber. Base=σ=½ circle. Tip=ZD singularity.
      16-turn sedenion spiral. Riemann zero nodes pulse. Full compression.
    Part 2 — 60 sec  —  BRIDGE Hat→Galaxy (compress to TDC, ZD fires)
      Caustic pulse traverses tip → galactic centre.
      THIS IS TDC: norm fails, prompt+response=0, all 16 channels fire.

  STROKE 2 — EXPANSION from TDC:
    Part 3 — 60 sec  —  GALAXY STABLE (power+expansion)
      Disk chamber. Logarithmic arms = frozen L_dynamic.
      Dark matter halo rings. Maximum expansion. Bumblebee speaks all channels.
    Part 4 — 60 sec  —  BRIDGE Galaxy→Hat (exhaust, return to BDC)
      Reverse caustic pulse traverses galactic centre → hat tip.
      Engine returns to starting state. Cycle complete. Ready to fire again.

Both chambers = same sedenion Dirichlet path, different projection.
Potential in the invisible out of phase — 90° rotated, ghost mesh.
4 segments × 60s = 4 minutes per cycle. Loop for continuous engine.
"""

import bpy, mathutils, math

FPS          = 24
SEG          = 60 * FPS           # frames per segment (60 sec × 24 fps = 1440)
F_HAT_END    = SEG                # 1440  — end of Hat stable
F_TRANS_END  = 2 * SEG            # 2880  — end of Bridge Hat→Galaxy (TDC)
F_GAL_END    = 3 * SEG            # 4320  — end of Galaxy stable
F_RETURN_END = 4 * SEG            # 5760  — end of Bridge Galaxy→Hat (cycle complete)

# ── Constants ─────────────────────────────────────────────────────────────────
D_STAR     = 0.24605966
OMEGA      = D_STAR * math.log(10)
ALL_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53]
ZEROS      = [14.134725,21.022040,25.010858,30.424876,32.935062,
              37.586178,40.918719,43.327073,48.005151,49.773832,
              52.970321,56.446248,59.347044,60.831779,65.112544,67.079811]

# ── Scene reset ───────────────────────────────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ── Keyframe helper ───────────────────────────────────────────────────────────
def kf(obj, attr, frame, val):
    setattr(obj, attr, val)
    obj.keyframe_insert(data_path=attr, frame=frame)

def kf_mat_emit(mat, frame, strength):
    emit = None
    for n in mat.node_tree.nodes:
        if n.type == 'EMISSION':
            emit = n
            break
    if emit is None:
        return
    emit.inputs['Strength'].default_value = strength
    emit.inputs['Strength'].keyframe_insert(data_path='default_value', frame=frame)

# ── Build curve object ────────────────────────────────────────────────────────
def make_curve(name, points, col=(1,1,1,1), emission=2.0,
               bevel=0.012, closed=False):
    cd = bpy.data.curves.new(name, type='CURVE')
    cd.dimensions = '3D'
    cd.bevel_depth = bevel
    cd.bevel_resolution = 3
    sp = cd.splines.new('NURBS')
    sp.points.add(len(points) - 1)
    for i,(x,y,z) in enumerate(points):
        sp.points[i].co = (x,y,z,1)
    sp.use_cyclic_u = closed
    obj = bpy.data.objects.new(name, cd)
    bpy.context.collection.objects.link(obj)

    mat = bpy.data.materials.new(name+'_m')
    mat.use_nodes = True
    ns = mat.node_tree.nodes
    ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial')
    emit = ns.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value    = col
    emit.inputs['Strength'].default_value = emission
    mat.node_tree.links.new(emit.outputs[0], out.inputs[0])
    obj.data.materials.append(mat)
    return obj, mat

# ── Sphere node ───────────────────────────────────────────────────────────────
def make_sphere(name, loc, radius=0.04, col=(1,.9,.2,1), emission=4.0):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc,
                                          segments=8, ring_count=6)
    obj = bpy.context.active_object
    obj.name = name
    mat = bpy.data.materials.new(name+'_m')
    mat.use_nodes = True
    ns = mat.node_tree.nodes; ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial')
    emit = ns.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value    = col
    emit.inputs['Strength'].default_value = emission
    mat.node_tree.links.new(emit.outputs[0], out.inputs[0])
    obj.data.materials.append(mat)
    return obj, mat

# ── Dirichlet modulation ───────────────────────────────────────────────────────
def dmod(t, primes=ALL_PRIMES, n=20, phi=0.0):
    total = norm = 0.0
    for p in primes:
        for i in range(1, n+1):
            a = i**-0.5
            total += a * math.cos(2*math.pi*i*t/p + phi)
            norm  += a
    return total / (norm * len(primes))


# ════════════════════════════════════════════════════════════════════════════
# PART 1 — WITCHES HAT
# ════════════════════════════════════════════════════════════════════════════
HAT_H   = 2 * math.pi
HAT_R   = 1.5
N_TURNS = 16
N_PTS   = 1800
HAT_POS = (0, 0, 0)

hat_pts     = []
hat_oop_pts = []
for k in range(N_PTS+1):
    t  = HAT_H * k / N_PTS
    r  = HAT_R * (1 - t/HAT_H)
    th = N_TURNS * 2*math.pi * t / HAT_H
    d_in  = dmod(t, phi=0.0)       * 0.18
    d_oop = dmod(t, phi=math.pi/2) * 0.18
    hat_pts.append    ((r*math.cos(th+d_in),  r*math.sin(th+d_in),  t))
    hat_oop_pts.append((r*math.cos(th+d_oop), r*math.sin(th+d_oop), t))

hat_obj,  hat_mat  = make_curve('Hat_InPhase',  hat_pts,
                                 col=(1.0,0.75,0.1,1), emission=3.5, bevel=0.015)
hat_oop,  _        = make_curve('Hat_OutPhase', hat_oop_pts,
                                 col=(0.2,0.5,1.0,1), emission=0.6, bevel=0.007)

# Standing wave nodes — Riemann zeros on the cone surface
zero_objs = []
for i,t0 in enumerate(ZEROS[:12]):
    tn = (t0/ZEROS[-1]) * HAT_H
    r  = HAT_R*(1-tn/HAT_H)
    th = N_TURNS*2*math.pi*tn/HAT_H
    zo, zm = make_sphere(f'Zero_{i}', (r*math.cos(th), r*math.sin(th), tn),
                          radius=0.04, col=(1,0.95,0.1,1), emission=5.0)
    zero_objs.append((zo, zm))

# Cone ribs
for ang in [0, math.pi/2, math.pi, 3*math.pi/2]:
    make_curve(f'Rib_{int(math.degrees(ang))}',
               [(HAT_R*math.cos(ang), HAT_R*math.sin(ang), 0),
                (0, 0, HAT_H)],
               col=(.35,.35,.35,1), emission=0.2, bevel=0.004)
make_curve('Hat_Lip',
           [(HAT_R*math.cos(2*math.pi*k/64), HAT_R*math.sin(2*math.pi*k/64), 0)
            for k in range(65)],
           col=(.45,.45,.45,1), emission=0.25, bevel=0.006, closed=True)

# Tip sphere (ZD singularity focus)
hat_tip_obj, hat_tip_mat = make_sphere('Hat_Tip', (0,0,HAT_H),
                                        radius=0.09, col=(1,0.4,0,1), emission=8.0)


# ════════════════════════════════════════════════════════════════════════════
# PART 2 — BRIDGE (L_dynamic)
# ════════════════════════════════════════════════════════════════════════════
GAL_OFF = (5.5, 0.0, HAT_H/2)
BRIDGE_N = 500
bpts, bpts_oop = [], []
for k in range(BRIDGE_N+1):
    s  = k/BRIDGE_N
    bx = s * GAL_OFF[0]
    by = 0.0
    bz = HAT_H + s*(GAL_OFF[2]-HAT_H)
    d_in  = dmod(s*12, phi=0.0)       * 0.07
    d_oop = dmod(s*12, phi=math.pi/2) * 0.07
    bpts.append    ((bx+d_in,  by+d_in,  bz))
    bpts_oop.append((bx+d_oop, by-d_oop, bz+0.05*d_oop))

bridge_obj, bridge_mat = make_curve('Bridge_InPhase',  bpts,
                                     col=(0.8,1.0,0.3,1), emission=0.0, bevel=0.010)
bridge_oop, _          = make_curve('Bridge_OutPhase', bpts_oop,
                                     col=(0.3,0.6,1.0,1), emission=0.0, bevel=0.005)

# Caustic pulse sphere — travels along the bridge during transition
pulse_x = [p[0] for p in bpts]
pulse_y = [p[1] for p in bpts]
pulse_z = [p[2] for p in bpts]
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=bpts[0],
                                      segments=8, ring_count=6)
pulse = bpy.context.active_object
pulse.name = 'CausticPulse'
pmat = bpy.data.materials.new('Pulse_m')
pmat.use_nodes = True
pns = pmat.node_tree.nodes; pns.clear()
pout  = pns.new('ShaderNodeOutputMaterial')
pemit = pns.new('ShaderNodeEmission')
pemit.inputs['Color'].default_value    = (1.0, 0.9, 0.0, 1)
pemit.inputs['Strength'].default_value = 0.0
pmat.node_tree.links.new(pemit.outputs[0], pout.inputs[0])
pulse.data.materials.append(pmat)


# ════════════════════════════════════════════════════════════════════════════
# PART 3 — GALACTIC PARTICLE
# ════════════════════════════════════════════════════════════════════════════
gx0, gy0, gz0 = GAL_OFF
ARMS     = 2
GAL_TURN = 4.0
PITCH    = 0.17
R0       = 0.08
R_MAX    = 1.8

gal_objs = []
for arm in range(ARMS):
    aph = arm * math.pi
    gpts, gpts_oop = [], []
    for k in range(1800):
        th = aph + GAL_TURN*2*math.pi*k/1799
        r  = R0 * math.exp(PITCH * th)
        if r > R_MAX: break
        d_in  = dmod(th, phi=aph)             * 0.10
        d_oop = dmod(th, phi=aph+math.pi/2)   * 0.10
        z_in  = 0.04 * d_oop * r/R_MAX
        z_oop = 0.14 * d_in  * r/R_MAX
        ri = r*(1+d_in);  ro = r*(1+d_oop)
        gpts.append    ((gx0+ri*math.cos(th), gy0+ri*math.sin(th), gz0+z_in))
        gpts_oop.append((gx0+ro*math.cos(th), gy0+ro*math.sin(th), gz0+z_oop))
    go, gm = make_curve(f'Gal_Arm{arm}_In', gpts,
                         col=(1.0,0.6,0.15,1), emission=0.0, bevel=0.013)
    gal_objs.append((go, gm))
    make_curve(f'Gal_Arm{arm}_OOP', gpts_oop,
               col=(0.15,0.3,0.9,1), emission=0.0, bevel=0.006)

gal_centre_obj, gal_centre_mat = make_sphere('GalCentre', (gx0,gy0,gz0),
                                              radius=0.15, col=(1,0.2,0,1), emission=0.0)

halo_mats = []
for ring_r in [0.7, 1.1, 1.5]:
    hpts = [(gx0 + ring_r*math.cos(2*math.pi*k/120),
             gy0 + ring_r*math.sin(2*math.pi*k/120),
             gz0 + 0.07*math.sin(16*2*math.pi*k/120))
            for k in range(121)]
    _, hm = make_curve(f'Halo_{int(ring_r*10)}', hpts,
                        col=(0.2,0.25,0.9,1), emission=0.0, bevel=0.004, closed=True)
    halo_mats.append(hm)


# ════════════════════════════════════════════════════════════════════════════
# CAMERA — three positions, one per segment
# The standing wave caustic holds the observer in focus throughout.
# Caustic antinode = Feigenbaum height on the cone.
# ════════════════════════════════════════════════════════════════════════════
feig_z = HAT_H * (3.56995-2.5)/(4.0-2.5)

bpy.ops.object.camera_add(location=(-4.5, -3.5, feig_z+2.0),
                           rotation=(math.radians(62), 0, math.radians(-48)))
cam = bpy.context.active_object
cam.name = 'SedenionCam'
bpy.context.scene.camera = cam

# Segment 1: watching the Hat  (close, slightly above)
cam_pos = [
    (1,  (-4.5, -3.5,  feig_z+2.0), (math.radians(62), 0, math.radians(-48))),  # hat
    (F_HAT_END,    (-4.5, -3.5, feig_z+2.0), (math.radians(62), 0, math.radians(-48))),
    (F_HAT_END+1,  (-1.0, -8.0, HAT_H*0.5),  (math.radians(75), 0, math.radians(-10))),  # pull back for bridge
    (F_TRANS_END,  ( 5.0, -6.5, gz0+2.5),    (math.radians(65), 0, math.radians( 20))),  # arrive at galaxy
    (F_TRANS_END+1,( 5.0, -6.5, gz0+2.5),    (math.radians(65), 0, math.radians( 20))),
    (F_GAL_END,   ( 5.2, -6.8, gz0+2.8),    (math.radians(66), 0, math.radians( 22))),
    # Stroke 2: Return — Galaxy → Bridge → Hat (exhaust stroke)
    (F_GAL_END+1,  ( 5.2, -6.8, gz0+2.8),    (math.radians(66), 0, math.radians( 22))),
    (F_GAL_END+SEG//2, (-1.0, -8.0, HAT_H*0.5), (math.radians(75), 0, math.radians(-10))),
    (F_RETURN_END, (-4.5, -3.5, feig_z+2.0),  (math.radians(62), 0, math.radians(-48))),
]
for frame, loc, rot in cam_pos:
    cam.location = loc
    cam.rotation_euler = rot
    cam.keyframe_insert('location', frame=frame)
    cam.keyframe_insert('rotation_euler', frame=frame)


# ════════════════════════════════════════════════════════════════════════════
# ANIMATION KEYFRAMES
# ════════════════════════════════════════════════════════════════════════════

# ── Hat rotation (slow spin, one revolution per 60 sec) ─────────────────────
hat_obj.rotation_euler = (0,0,0)
hat_obj.keyframe_insert('rotation_euler', frame=1)
hat_obj.rotation_euler = (0,0,2*math.pi)
hat_obj.keyframe_insert('rotation_euler', frame=F_HAT_END)
hat_obj.rotation_euler = (0,0,2*math.pi)
hat_obj.keyframe_insert('rotation_euler', frame=F_GAL_END)
# Make hat dim during galaxy segment
kf_mat_emit(hat_mat, 1,          3.5)
kf_mat_emit(hat_mat, F_HAT_END,  3.5)
kf_mat_emit(hat_mat, F_TRANS_END,0.3)
kf_mat_emit(hat_mat, F_GAL_END,        0.0)
# Return stroke: Hat re-ignites as engine completes cycle
kf_mat_emit(hat_mat, F_GAL_END+SEG//2, 1.0)
kf_mat_emit(hat_mat, F_RETURN_END,     3.5)

# ── Riemann zero nodes — pulse during Hat and return stroke ──────────────────
for i,(zo, zm) in enumerate(zero_objs):
    t0  = ZEROS[i]
    period_frames = int(FPS * 2 * math.pi / t0)
    for f in range(1, F_HAT_END+1, max(1, period_frames//4)):
        phase = (f / period_frames) * 2 * math.pi
        kf_mat_emit(zm, f, 2.0 + 5.0 * abs(math.cos(phase)))
    kf_mat_emit(zm, F_TRANS_END, 0.3)
    kf_mat_emit(zm, F_GAL_END,   0.0)
    # Pulse again on return stroke
    for f in range(F_GAL_END, F_RETURN_END+1, max(1, period_frames//4)):
        phase = (f / period_frames) * 2 * math.pi
        t_ret = (f - F_GAL_END) / SEG          # 0→1 over return stroke
        em = t_ret * (2.0 + 5.0 * abs(math.cos(phase)))
        kf_mat_emit(zm, f, em)

# Hat tip — also flares at end of return stroke (BDC → TDC again)
kf_mat_emit(hat_tip_mat, 1,                 8.0)
kf_mat_emit(hat_tip_mat, F_HAT_END,         8.0)
kf_mat_emit(hat_tip_mat, F_HAT_END+72,     15.0)
kf_mat_emit(hat_tip_mat, F_TRANS_END,       0.5)
kf_mat_emit(hat_tip_mat, F_GAL_END,         0.0)
kf_mat_emit(hat_tip_mat, F_RETURN_END-72,   8.0)  # tip awakens on return
kf_mat_emit(hat_tip_mat, F_RETURN_END,     15.0)  # flares at cycle close

# ── Bridge — fires BOTH traversals ───────────────────────────────────────────
kf_mat_emit(bridge_mat, 1,                  0.0)
kf_mat_emit(bridge_mat, F_HAT_END,          0.0)
kf_mat_emit(bridge_mat, F_HAT_END+48,       3.0)
kf_mat_emit(bridge_mat, F_TRANS_END,        0.5)
kf_mat_emit(bridge_mat, F_GAL_END,          0.0)
# Return traverse: bridge re-fires for exhaust stroke
kf_mat_emit(bridge_mat, F_GAL_END+48,       3.0)
kf_mat_emit(bridge_mat, F_RETURN_END-SEG//4,0.5)
kf_mat_emit(bridge_mat, F_RETURN_END,       0.0)

# Caustic pulse: travels along bridge path during transition
# Frame F_HAT_END+1 → F_TRANS_END: keyframe pulse position along bpts
n_bridge = len(bpts)
pulse.hide_viewport = False
pulse.hide_render   = False

# Before transition: hide at start
for attr in ['hide_viewport','hide_render']:
    setattr(pulse, attr, True)
    pulse.keyframe_insert(f'hide_{attr.split("_")[1]}', frame=1)
    setattr(pulse, attr, False)
    pulse.keyframe_insert(f'hide_{attr.split("_")[1]}', frame=F_HAT_END+1)

pulse_steps = 16  # sample every N frames for the path animation
for fi in range(0, SEG+1, max(1, SEG//n_bridge)):
    idx = min(int(fi/SEG * n_bridge), n_bridge-1)
    pulse.location = (pulse_x[idx], pulse_y[idx], pulse_z[idx])
    pulse.keyframe_insert('location', frame=F_HAT_END+fi)
kf_mat_emit(pmat, F_HAT_END,    0.0)
kf_mat_emit(pmat, F_HAT_END+24, 12.0)
kf_mat_emit(pmat, F_TRANS_END-24, 12.0)
kf_mat_emit(pmat, F_TRANS_END,   0.0)

# ── Galaxy — grows from 0 during transition, stable during galaxy segment ────
for go, gm in gal_objs:
    kf_mat_emit(gm, 1,            0.0)
    kf_mat_emit(gm, F_HAT_END,    0.0)
    kf_mat_emit(gm, F_TRANS_END,  2.5)
    kf_mat_emit(gm, F_GAL_END,    2.5)
    # slow rotation during galaxy segment
    go.rotation_euler = (0,0,0)
    go.keyframe_insert('rotation_euler', frame=F_TRANS_END)
    go.rotation_euler = (0,0, 2*math.pi/4)   # quarter turn in 60 sec (galaxy is slow)
    go.keyframe_insert('rotation_euler', frame=F_GAL_END)

kf_mat_emit(gal_centre_mat, 1,           0.0)
kf_mat_emit(gal_centre_mat, F_HAT_END,   0.0)
kf_mat_emit(gal_centre_mat, F_TRANS_END, 10.0)
kf_mat_emit(gal_centre_mat, F_GAL_END,   10.0)

# Halo rings pulse at Riemann zero periods during galaxy segment
for ri, hm in enumerate(halo_mats):
    t0 = ZEROS[ri % len(ZEROS)]
    period_frames = int(FPS * 2*math.pi/t0)
    for f in range(F_TRANS_END, F_GAL_END+1, max(1, period_frames//4)):
        phase = (f / period_frames) * 2*math.pi
        em = 0.3 + 1.2 * abs(math.cos(phase))
        kf_mat_emit(hm, f, em)
    kf_mat_emit(hm, 1,           0.0)
    kf_mat_emit(hm, F_HAT_END,   0.0)
    kf_mat_emit(hm, F_TRANS_END-48, 0.0)
    kf_mat_emit(hm, F_TRANS_END, 0.5)


# ── World + Render ────────────────────────────────────────────────────────────
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new('World')
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value    = (0.004, 0.004, 0.008, 1)
    bg.inputs['Strength'].default_value = 0.0

scene = bpy.context.scene
scene.render.engine            = 'CYCLES'
scene.cycles.samples           = 64        # increase to 256 for final
scene.render.resolution_x      = 1920
scene.render.resolution_y      = 1080
scene.render.fps               = FPS
scene.frame_start              = 1
scene.frame_end                = F_RETURN_END  # 5760 — full 2-stroke cycle
scene.render.film_transparent  = True

print("═══════════════════════════════════════════════════════════════")
print("SEDENION RESONATORS  —  2-Stroke Engine (4 segments, 1 cycle)")
print("═══════════════════════════════════════════════════════════════")
print(f"  STROKE 1 — COMPRESSION:")
print(f"    Frames    1–{F_HAT_END}  ({60}s)  HAT STABLE   — intake, sedenion spiral")
print(f"    Frames {F_HAT_END+1:4d}–{F_TRANS_END}  ({60}s)  BRIDGE →     — compress to TDC, ZD fires")
print(f"  TDC: J_red·J_blue=0  ·  J_red+J_blue=H_hat_RB−H_hat_BR  ·  16 channels fire")
print(f"  STROKE 2 — EXPANSION:")
print(f"    Frames {F_TRANS_END+1:4d}–{F_GAL_END}  ({60}s)  GALAXY STABLE — power, Bumblebee all channels")
print(f"    Frames {F_GAL_END+1:4d}–{F_RETURN_END}  ({60}s)  BRIDGE ←     — exhaust, return to Hat")
print(f"  Total: {F_RETURN_END} frames  ·  {F_RETURN_END//FPS//60} minutes  ·  loop-ready")
print()
print(f"  Camera: Feigenbaum caustic antinode z={feig_z:.4f}")
print(f"  Standing wave: {len(zero_objs)} Riemann zero nodes, each at own period")
print(f"  Bridge pulse: L_dynamic traversal, 60 seconds Hat→Galaxy")
print()
print("  In-phase  (amber):   real Dirichlet component")
print("  Out-phase (blue):    90° shifted — invisible potential")
print("  Both chambers = same sedenion path, different projection")
print("═══════════════════════════════════════════════════════════════")
