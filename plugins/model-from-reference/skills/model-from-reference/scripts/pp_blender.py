"""Сессионный инструментарий для регламента box modelling в Blender.

Ставится в сессию ОДИН раз и живёт в ``sys.modules`` до перезапуска Blender.
Дальше каждый такт цикла шага — короткий вызов по имени, а не новый скрипт.

Проверено: ``sys.modules`` переживает вызовы ``execute_blender_code``, голые
``globals()`` — нет. Поэтому модуль, а не функции в коде вызова.

Установка (одним вызовом ``execute_blender_code``)::

    import sys, types, pathlib
    p = "<repo>/rules/methods/tools/pp_blender.py"
    mod = types.ModuleType("pp"); mod.__file__ = p
    exec(compile(pathlib.Path(p).read_text(encoding="utf-8"), p, "exec"), mod.__dict__)
    sys.modules["pp"] = mod
    result = {"установлено": mod.VERSION, "функции": sorted(mod.__all__)}

Использование::

    import sys; pp = sys.modules["pp"]
    result = pp.section(pp.obj("MODEL_центр"), 1561.2)
"""

import math
import os

import bmesh
import bpy
from mathutils import Euler, Vector

VERSION = "3.4"

__all__ = [
    "obj", "evaluated", "cage", "mm_per_unit",
    "section", "bbox", "gauge",
    "budget", "topology", "seam", "mods", "scene_report",
    "view", "channel", "shots", "orbit",
    "snapshot", "restore", "points",
    "guide", "ring_positions", "ring_phis", "rings", "ring_order", "place_ring",
    "crease_arc", "extend", "ref_measure", "smoothness", "frame_scale",
]

GEOM_TYPES = {"MESH", "CURVE", "SURFACE", "META", "FONT"}

# Оси плоскости сечения: (индекс i, индекс j, имя по i, имя по j).
# Габарит меряется в плоскости реза, а не по фиксированным X и Y: иначе при
# axis="X" «ширина» тождественно равна нулю и сверка врёт.
_AXES = {
    "X": (1, 2, "глубина_мм", "высота_мм"),
    "Y": (0, 2, "ширина_мм", "высота_мм"),
    "Z": (0, 1, "ширина_мм", "глубина_мм"),
}
_NORMAL = {"X": 0, "Y": 1, "Z": 2}

# Допуск «вершина лежит ровно на плоскости» для реза. Нулевой допуск при резе
# по кольцу каркаса даёт неопределённый знак у вершин кольца: часть уходит в
# «внутрь», часть во «вне», и контур рвётся.
PLANE_EPS = 1e-6


# ---------------------------------------------------------------- служебное

def mm_per_unit():
    """Сколько миллиметров в одной единице сцены.

    Жёсткая тысяча верна только при ``scale_length == 1.0``. В сцене, собранной
    под другой масштаб, все замеры уехали бы в этот множитель, оставаясь
    правдоподобными.
    """
    return 1000.0 * bpy.context.scene.unit_settings.scale_length


def obj(name):
    """Объект по имени. Падает громко, а не возвращает None."""
    o = bpy.data.objects.get(name)
    if o is None:
        raise KeyError(f"объекта «{name}» в сцене нет; "
                       f"есть: {sorted(x.name for x in bpy.data.objects)}")
    return o


def cage(ob):
    """Каркас объекта с проверкой, что он вообще читается.

    В режиме редактирования ``ob.data`` не синхронизирован с правками: отчёт
    вернёт устаревшие, но правдоподобные числа. Худший вид отказа, поэтому
    здесь он превращается в громкую ошибку.
    """
    if ob.type != "MESH":
        raise TypeError(f"«{ob.name}» типа {ob.type}: каркаса-меша нет")
    if ob.mode != "OBJECT":
        raise RuntimeError(f"«{ob.name}» в режиме {ob.mode}: правки не сброшены "
                           f"в ob.data, отчёт соврёт. Выйдите в Object Mode")
    return ob.data


class evaluated:
    """Итоговая поверхность: результат преобразований, а не каркас.

    Замер по каркасу недействителен — аппроксимирующая схема Catmull-Clark
    ужимает объём, каркас сидит снаружи результата.

    **Уровень.** Депсграф контекста — вьюпортный, поэтому читается уровень
    показа, а не выдачи. Если они разошлись, замер снят не с того, что уйдёт
    наружу; регламент требует их равенства, и здесь это проверяется.
    """

    def __init__(self, ob, strict_levels=True):
        if ob.type not in GEOM_TYPES:
            raise TypeError(f"«{ob.name}» типа {ob.type}: поверхности из него не выйдет")
        if ob.mode != "OBJECT":
            raise RuntimeError(f"«{ob.name}» в режиме {ob.mode}: замер соврёт. "
                               f"Выйдите в Object Mode")
        if strict_levels:
            for m in ob.modifiers:
                if m.type == "SUBSURF" and m.levels != m.render_levels:
                    raise RuntimeError(
                        f"«{ob.name}»: подразделение «{m.name}» показывает уровень "
                        f"{m.levels}, а выдаёт {m.render_levels}. Замер снимается по "
                        f"вьюпортному — уравняйте уровни (регламент, M2 п. 3)")
                if m.type in {"SUBSURF", "MIRROR"} and not m.show_viewport:
                    raise RuntimeError(
                        f"«{ob.name}»: «{m.name}» выключен в показе, замер пойдёт "
                        f"мимо него")
        self.ob = ob
        self.ev = None

    def __enter__(self):
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        self.ev = self.ob.evaluated_get(dg)
        return self.ev, self.ev.to_mesh()

    def __exit__(self, *exc):
        if self.ev is not None:
            self.ev.to_mesh_clear()
        return False


def _world_bmesh(ob):
    """bmesh итоговой поверхности в мировых координатах. Освобождать вызывающему."""
    with evaluated(ob) as (ev, me):
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.transform(ev.matrix_world)
    return bm


def _components(verts):
    """Связные компоненты по рёбрам — число раздельных контуров сечения.

    Одиночные вершины без рёбер компонентой **не** считаются: рез, касательный
    к поверхности, оставляет такие точки, и без этого отбора касание выглядело
    бы как второй контур, то есть как зона разворота, которой нет.
    """
    pool = [v for v in verts if v.link_edges]
    seen, groups = set(), []
    for v in pool:
        if v in seen:
            continue
        comp, stack = [], [v]
        while stack:
            w = stack.pop()
            if w in seen:
                continue
            seen.add(w)
            comp.append(w)
            for e in w.link_edges:
                other = e.other_vert(w)
                if other not in seen:
                    stack.append(other)
        groups.append(comp)
    return groups, len(verts) - len(pool)


def _area3d():
    """Область 3D-вида — тем же правилом, что и инструмент снимка сервера.

    Сервер берёт ``context.area``, если её ``ui_type`` совпал, иначе **самую
    большую** подходящую. Первая попавшаяся не годится: в раскладке с двумя
    видами ракурс встанет в одной области, а снимок придёт из другой.
    """
    screen = bpy.context.screen
    areas = [a for a in screen.areas if a.ui_type == "VIEW_3D"]
    if not areas:
        raise RuntimeError("в текущем окне нет области 3D-вида")
    ca = getattr(bpy.context, "area", None)
    if ca is not None and ca.ui_type == "VIEW_3D":
        return ca, len(areas)
    return max(areas, key=lambda a: a.width * a.height), len(areas)


# ---------------------------------------------------------------- измерение

def _cut(bm_src, coord_mm, axis, mm):
    """Один рез копии исходного bmesh. Возвращает словарь замера."""
    i, j, name_i, name_j = _AXES[axis]
    no = Vector((0.0, 0.0, 0.0))
    no[_NORMAL[axis]] = 1.0
    bm = bm_src.copy()
    try:
        bmesh.ops.bisect_plane(
            bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
            plane_co=no * (coord_mm / mm), plane_no=no,
            dist=PLANE_EPS, clear_inner=True, clear_outer=True)
        vs = [v for v in bm.verts if v.is_valid]
        groups, loose = _components(vs)
        if not groups:
            return {"ось": axis, "координата_мм": coord_mm, "контуров": 0,
                    "пусто": True, "касательных_точек": loose}

        def box(vv):
            a = [v.co[i] for v in vv]
            b = [v.co[j] for v in vv]
            return {name_i: round((max(a) - min(a)) * mm, 2),
                    name_j: round((max(b) - min(b)) * mm, 2),
                    f"центр_{name_i}": round((max(a) + min(a)) / 2 * mm, 2),
                    f"центр_{name_j}": round((max(b) + min(b)) / 2 * mm, 2)}

        flat = [v for g in groups for v in g]
        out = {"ось": axis, "координата_мм": coord_mm, "контуров": len(groups),
               "вершин": len(flat), "касательных_точек": loose, "пусто": False}
        out.update(box(flat))
        if len(groups) > 1:
            out["по_контурам"] = [box(g) for g in groups]
        return out
    finally:
        bm.free()


def section(ob, coord_mm, axis="Z"):
    """Сечение итоговой поверхности плоскостью, перпендикулярной ``axis``.

    Габарит **в плоскости реза**, центр и **число раздельных контуров**. Число
    контуров — главная проверка зоны разворота: два контура означают, что
    поверхность заворачивается.

    При двух и более контурах поля габарита описывают **объединение** — размах
    через пустоту между ними. Сравнивать его с замером сечения нельзя;
    поконтурные габариты лежат в ``по_контурам``.

    Проверено: тор осью вдоль Y даёт 2 контура через дырку и 1 ниже неё;
    половина куба с зеркалом даёт 1 контур.
    """
    mm = mm_per_unit()
    bm = _world_bmesh(ob)
    try:
        return _cut(bm, coord_mm, axis, mm)
    finally:
        bm.free()


def bbox(ob):
    """Габаритная коробка **итоговой поверхности** в миллиметрах.

    Общий габарит детали — одно из двух числовых исключений регламента.
    ``ob.dimensions`` не годится: оно снято с каркаса, а каркас сидит снаружи
    результата. Поворот и масштаб объекта учтены.
    """
    mm = mm_per_unit()
    with evaluated(ob) as (ev, me):
        if not me.vertices:
            return {"пусто": True}
        m = ev.matrix_world
        pts = [m @ v.co for v in me.vertices]
        lo = [min(p[k] for p in pts) for k in range(3)]
        hi = [max(p[k] for p in pts) for k in range(3)]
    return {"ширина_мм": round((hi[0] - lo[0]) * mm, 2),
            "глубина_мм": round((hi[1] - lo[1]) * mm, 2),
            "высота_мм": round((hi[2] - lo[2]) * mm, 2),
            "центр_мм": [round((hi[k] + lo[k]) / 2 * mm, 2) for k in range(3)],
            "низ_мм": round(lo[2] * mm, 2), "верх_мм": round(hi[2] * mm, 2)}


def gauge(ob, levels, tol_mm, axis="Z"):
    """Сверка с разметкой: ``levels`` = ``[{z_mm, width_mm, depth_mm, label}]``.

    Итоговая поверхность строится **один раз** на всю сверку, а не заново на
    каждый уровень.

    Три исхода на уровень, и все три видны в сводке:

    - **пусто** — модель до этой координаты не доходит. Отказ, а не пропуск:
      это самый грубый брак, и молча пройти он не должен;
    - **два и более контура** — зона разворота. Сравнение с замером сечения
      здесь бессмысленно, уровень уходит в ``разворотов`` и разбирается глазом;
    - **один контур** — обычная сверка.

    Правок не делает: что чинить, решает исполнитель.
    """
    mm = mm_per_unit()
    bm = _world_bmesh(ob)
    rows, bad_levels, bad_values, empty, splits = [], 0, 0, 0, 0
    try:
        for lv in levels:
            s = _cut(bm, lv["z_mm"], axis, mm)
            r = {"label": lv.get("label", ""), "z_mm": lv["z_mm"],
                 "контуров": s.get("контуров", 0)}
            if s.get("пусто"):
                r.update({"пусто": True, "в_допуске": False})
                empty += 1
                bad_levels += 1
                rows.append(r)
                continue
            if s["контуров"] > 1:
                r.update({"разворот": True, "в_допуске": None,
                          "по_контурам": s.get("по_контурам")})
                splits += 1
                rows.append(r)
                continue
            level_bad = False
            for key, name in (("width_mm", "ширина_мм"), ("depth_mm", "глубина_мм")):
                want = lv.get(key)
                if want is None or s.get(name) is None:
                    continue
                d = s[name] - want
                ok = abs(d) <= tol_mm
                r[name] = {"замер": want, "модель": s[name],
                           "расхождение": round(d, 2), "в_допуске": ok}
                if not ok:
                    bad_values += 1
                    level_bad = True
            r["в_допуске"] = not level_bad
            bad_levels += int(level_bad)
            rows.append(r)
    finally:
        bm.free()
    return {"допуск_мм": tol_mm, "уровней": len(rows),
            "уровней_вне_допуска": bad_levels, "замеров_вне_допуска": bad_values,
            "пустых_сечений": empty, "разворотов": splits, "строки": rows}


# ---------------------------------------------------------------- отчёты

def smoothness(ob, z0_mm, z1_mm, step_mm=2.0, axis="Z"):
    """Первая и вторая разность обвода по высоте — **подсказка** об изломе.

    Положение может сойтись с образцом до миллиметра, а поверхность при этом
    читаться изломом: глаз видит разрыв производной, замер габарита — нет.
    Здесь считается вторая разность ширины и переднего края; всплеск на её
    графике показывает, ГДЕ смотреть.

    **Приговор выносит глаз, не эта функция.** Она груба по трём причинам:
    берёт только габарит сечения, то есть две крайние точки из полусотни;
    ничего не знает о боках и о том, что между крайними точками; и всплеск на
    ней бывает законным — линия челюсти есть излом по существу, а не дефект.
    Осмотр в отражающем канале (11.2) она не заменяет и заменить не может.

    Итоговая поверхность строится один раз на весь проход, а не заново на
    каждый рез.
    """
    mm = mm_per_unit()
    bm0 = _world_bmesh(ob)
    try:
        zs, w, f, b = [], [], [], []
        z = z0_mm
        while z <= z1_mm + 1e-6:
            s = _cut(bm0, z, axis, mm)
            zs.append(round(z, 1))
            if s.get("пусто") or s.get("контуров", 0) < 1:
                w.append(None); f.append(None); b.append(None)
            else:
                i, j, name_i, name_j = _AXES[axis]
                w.append(s[name_i])
                f.append(s[f"центр_{name_j}"] - s[name_j] / 2)
                b.append(s[f"центр_{name_j}"] + s[name_j] / 2)
            z += step_mm
    finally:
        bm0.free()

    def d2(a):
        out = [None] * len(a)
        for k in range(1, len(a) - 1):
            if None in (a[k - 1], a[k], a[k + 1]):
                continue
            out[k] = round((a[k + 1] - 2 * a[k] + a[k - 1]) / (step_mm ** 2), 4)
        return out

    return {"z": zs, "ширина": w, "перёд": f, "зад": b,
            "d2_ширины": d2(w), "d2_переда": d2(f)}


def budget(ob, share=None):
    """Полигоны каркаса против итоговой поверхности и вердикт по бюджету.

    Отчёт снимается **с результата преобразований**. Снятый с каркаса, он
    занижен во столько раз, во сколько подразделение множит грани.

    ``share`` — доля детали в диапазоне: ``(min_tris, max_tris)``. Без неё
    вердикта нет, и отчёт остаётся числом без ветки отказа.
    """
    me_cage = cage(ob)
    with evaluated(ob) as (_ev, me):
        fin_v, fin_p = len(me.vertices), len(me.polygons)
        tris = sum(max(len(p.vertices) - 2, 0) for p in me.polygons)
    n = len(me_cage.polygons)
    out = {"каркас": {"вершин": len(me_cage.vertices), "полигонов": n},
           "итог": {"вершин": fin_v, "полигонов": fin_p, "треугольников": tris},
           "множитель": round(fin_p / n, 2) if n else None}
    if share:
        lo, hi = share
        out["доля"] = {"min": lo, "max": hi}
        out["вердикт"] = ("ниже нижней границы" if tris < lo else
                          "вне диапазона" if tris > hi else
                          "у верхней границы" if tris > lo + 0.9 * (hi - lo) else
                          "в диапазоне")
        out["запас_до_верхней"] = hi - tris
    return out


def topology(ob, seam_axis="X", seam_tol_mm=0.01):
    """Проверки топологии — по каркасу и по итогу, с адресами находок.

    Полюс считается **по граням**, а не по рёбрам: у вершины на открытой
    границе рёбер и граней разное число, и счёт по рёбрам даёт ложные полюса.

    Вершины шва при работе с зеркалом лежат на **открытой границе** каркаса,
    поэтому фильтр «не граничная» их полностью съедает. Шов — см. :func:`seam`.

    «Неманифолдное ребро» здесь — ребро с **тремя и более** гранями. Свойство
    ``is_manifold`` ложно и для граничного ребра, и для проволочного, поэтому
    прямой подсчёт по нему всегда завышен на величину открытой границы.
    """
    mm = mm_per_unit()
    me = cage(ob)
    by_sides = {}
    for p in me.polygons:
        by_sides[len(p.vertices)] = by_sides.get(len(p.vertices), 0) + 1

    ax = _NORMAL[seam_axis]
    tol = seam_tol_mm / mm
    bm = bmesh.new()
    try:
        bm.from_mesh(me)
        poles, loose = [], 0
        for v in bm.verts:
            if not v.link_faces:
                loose += 1
                continue
            if v.is_boundary:
                continue                      # граница и шов — забота seam()
            if len(v.link_faces) != 4:
                poles.append({"степень": len(v.link_faces),
                              "мм": [round(c * mm, 1) for c in v.co]})
        cage_boundary = sum(1 for e in bm.edges if e.is_boundary)
        ngon_faces = [{"сторон": len(f.verts),
                       "мм": [round(c * mm, 1) for c in f.calc_center_median()]}
                      for f in bm.faces if len(f.verts) >= 5]
    finally:
        bm.free()

    with evaluated(ob) as (_ev, me_ev):
        bm2 = bmesh.new()
        try:
            bm2.from_mesh(me_ev)
            open_edges = sum(1 for e in bm2.edges if len(e.link_faces) == 1)
            wire_edges = sum(1 for e in bm2.edges if len(e.link_faces) == 0)
            multi_edges = sum(1 for e in bm2.edges if len(e.link_faces) > 2)
        finally:
            bm2.free()

    return {"каркас_по_сторонам": dict(sorted(by_sides.items())),
            "n_угольников": len(ngon_faces), "адреса_n_угольников": ngon_faces[:20],
            "треугольников": by_sides.get(3, 0),
            "рыхлых_вершин": loose,
            "каркас_открытых_рёбер": cage_boundary,
            "итог_открытых_рёбер": open_edges,
            "итог_проволочных_рёбер": wire_edges,
            "итог_рёбер_с_3+_гранями": multi_edges,
            "полюсов_внутри": len(poles), "адреса_полюсов": poles[:30]}


def seam(ob, axis="X", tol_mm=0.01):
    """Разбор шва симметрии на каркасе половины детали.

    Проверяет то, что требует операция «установить отражение»: вершины шва не
    отходят от плоскости, за плоскость никто не ушёл, удвоенных вершин нет,
    полюсов на шве нет.

    Законная степень вершины шва на каркасе половины — **три**: после сварки
    зеркалом она становится четвёркой. Полюс на шве — степень, отличная от трёх.
    """
    mm = mm_per_unit()
    me = cage(ob)
    ax = _NORMAL[axis]
    tol = tol_mm / mm
    i, j = [k for k in range(3) if k != ax]
    bm = bmesh.new()
    try:
        bm.from_mesh(me)
        on_seam = [v for v in bm.verts if abs(v.co[ax]) <= tol]
        near = [v for v in bm.verts if tol < abs(v.co[ax]) <= tol * 10]
        crossed = [v for v in bm.verts if v.co[ax] < -tol]
        poles = [{"степень": len(v.link_edges),
                  "мм": [round(c * mm, 1) for c in v.co]}
                 for v in on_seam if len(v.link_edges) != 3]
        seen, dup = set(), 0
        for v in on_seam:
            k = (round(v.co[i] / tol), round(v.co[j] / tol))
            if k in seen:
                dup += 1
            seen.add(k)
        worst = max((abs(v.co[ax]) for v in on_seam), default=0.0)
    finally:
        bm.free()
    return {"ось": axis, "допуск_мм": tol_mm,
            "вершин_на_шве": len(on_seam),
            "макс_отклонение_мм": round(worst * mm, 4),
            "почти_на_шве": len(near),
            "ушли_за_плоскость": len(crossed),
            "удвоенных": dup,
            "полюсов_на_шве": len(poles), "адреса_полюсов": poles[:20]}


def mods(ob):
    """Стек преобразований: порядок, уровни, ключевые свойства.

    Отражение действует **раньше** сглаживания. Порядок задаётся индексом, и
    поставленное вторым отражение даёт неверный шов при внешне верной модели.
    """
    mm = mm_per_unit()
    out = []
    levels_ok = True
    for k, m in enumerate(ob.modifiers):
        d = {"индекс": k, "имя": m.name, "тип": m.type,
             "показ": m.show_viewport, "выдача": m.show_render}
        if m.type == "MIRROR":
            d.update({"оси": list(m.use_axis), "прижим": m.use_clip,
                      "сварка": m.use_mirror_merge,
                      "порог_мм": round(m.merge_threshold * mm, 3),
                      "объект_отражения": m.mirror_object.name if m.mirror_object else None})
        if m.type == "SUBSURF":
            d.update({"схема": m.subdivision_type, "уровень_показа": m.levels,
                      "уровень_выдачи": m.render_levels, "на_каркасе": m.show_on_cage})
            if m.levels != m.render_levels:
                levels_ok = False
        out.append(d)
    order = [m["тип"] for m in out]
    ok = ("MIRROR" not in order or "SUBSURF" not in order
          or order.index("MIRROR") < order.index("SUBSURF"))
    return {"стек": out, "порядок": order,
            "отражение_раньше_сглаживания": ok,
            "уровни_показа_и_выдачи_равны": levels_ok,
            "запечённых": 0 if out else None}


def scene_report():
    """Только то, чего не даёт `get_objects_summary`: единицы, масштаб, файл.

    Состав сцены по коллекциям и объектам берётся инструментом осмотра сервера,
    а не отсюда: дублировать его — то самое избыточное действие.
    """
    geo = [o for o in bpy.data.objects if o.type in GEOM_TYPES]
    us = bpy.context.scene.unit_settings
    return {"геометрических_объектов": len(geo),
            "единицы": us.system, "длина": us.length_unit,
            "масштаб": round(us.scale_length, 6),
            "мм_в_единице": mm_per_unit(),
            "файл": bpy.data.filepath, "изменён": bpy.data.is_dirty}


def ring_phis(half_w_mm, front_mm, back_mm, n_verts, steps=4000):
    """Углы равной дуги для кольца — **общий** параметр для группы колец.

    Равная дуга, посчитанная заново для каждого кольца, ломает меридианы, как
    только соседние кольца различаются пропорциями. Вершина сидит на четверти
    дуги своего эллипса, но у соседа эта четверть приходится на другое место в
    пространстве: меридиан идёт наискось, лента граней получает сдвиг по всему
    обходу.

    Проверено дорого. В зоне разворота перёд уезжает между соседними кольцами
    на пятьдесят миллиметров, у эллипса смещается центр — и вместе с ним едут
    боковые вершины, которым двигаться не надо. На поверхности это читается
    воротником и полкой, а на отражающем канале — завихрениями.

    Считать распределение один раз и передавать всей группе (``phis`` в
    :func:`ring_positions`) — значит держать меридианы прямыми.
    """
    a, b = half_w_mm, (back_mm - front_mm) / 2.0
    if n_verts < 2 or a <= 0 or b <= 0:
        return [0.0] * max(n_verts, 0)
    pts, cum, prev = [], [0.0], None
    for i in range(steps + 1):
        th = math.pi * i / steps
        x, y = a * math.sin(th), -b * math.cos(th)
        pts.append((x, y))
        if prev is not None:
            cum.append(cum[-1] + math.hypot(x - prev[0], y - prev[1]))
        prev = (x, y)
    total = cum[-1]
    out, j = [], 0
    for k in range(n_verts):
        target = total * k / (n_verts - 1)
        while j < steps - 1 and cum[j + 1] < target:
            j += 1
        j = min(j, steps - 1)
        seg = cum[j + 1] - cum[j]
        u = 0.0 if seg <= 0 else (target - cum[j]) / seg
        out.append(math.pi * (j + u) / steps)
    return out


def _superell(a, cy, b, th, n_front, n_back):
    """Точка суперэллипса по параметру ``th`` (0 — перёд, π — зад).

    При показателе 2 это обычный эллипс. Больше двух — перёд, зад и бока
    уплощаются, а углы между ними скругляются: так устроено сечение грудной
    клетки и таза, и эллипсом оно не описывается, отчего торс читается бочкой.

    Показатели переда и зада задаются порознь: у человека перёд груди площе
    спины.
    """
    s, c = math.sin(th), math.cos(th)
    n = n_front if c >= 0.0 else n_back
    p = 2.0 / n
    x = a * (abs(s) ** p)
    y = cy - b * (abs(c) ** p) * (1.0 if c >= 0.0 else -1.0)
    return x, y


def ring_positions(half_w_mm, front_mm, back_mm, n_verts, steps=4000, phis=None,
                   n_front=2.0, n_back=2.0):
    """Точки половины кольца по эллипсу, распределённые по **равной дуге**.

    Равный шаг по углу на эллипсе даёт неравный шаг по дуге: у узкого конца
    вершины сгущаются, на боках растягиваются. На окружности разницы нет, на
    вытянутом сечении она доходит до трёх раз — и числовая проверка сечения
    её не видит вовсе, потому что меряет габарит, а не распределение вдоль
    контура.

    Возвращает ``n_verts`` пар (x, y) в миллиметрах, от переда к заду; первая
    и последняя лежат на плоскости симметрии (x = 0).

    ``phis`` — готовые углы (см. :func:`ring_phis`). Передавать их **обязательно**
    там, где соседние кольца сильно различаются пропорциями: иначе каждое
    кольцо разложится по своей дуге, и меридианы пойдут наискось.
    """
    a = half_w_mm
    cy = (front_mm + back_mm) / 2.0
    b = (back_mm - front_mm) / 2.0
    if n_verts < 1:
        return []
    if phis is not None:
        out = []
        for k, th in enumerate(phis[:n_verts]):
            x, y = _superell(a, cy, b, th, n_front, n_back)
            out.append((0.0 if k in (0, n_verts - 1) else x, y))
        return out
    if n_verts == 1:
        return [(0.0, cy)]              # одна вершина — на плоскости симметрии
    if n_verts == 2:
        return [(0.0, front_mm), (0.0, back_mm)]
    pts, cum, prev = [], [0.0], None
    for i in range(steps + 1):
        th = math.pi * i / steps
        x, y = _superell(a, cy, b, th, n_front, n_back)
        pts.append((x, y))
        if prev is not None:
            cum.append(cum[-1] + math.hypot(x - prev[0], y - prev[1]))
        prev = (x, y)
    total = cum[-1]
    out, j = [], 0
    for k in range(n_verts):
        target = total * k / (n_verts - 1)
        while j < steps - 1 and cum[j + 1] < target:
            j += 1
        j = min(j, steps - 1)          # последняя точка: индекс не должен уйти за хвост
        seg = cum[j + 1] - cum[j]
        u = 0.0 if seg <= 0 else (target - cum[j]) / seg
        x = pts[j][0] + (pts[j + 1][0] - pts[j][0]) * u
        y = pts[j][1] + (pts[j + 1][1] - pts[j][1]) * u
        out.append((0.0 if k in (0, n_verts - 1) else x, y))
    return out


# ------------------------------------------------------------ обход колец

def _seed_ring(bm, seam_axis="X", seam_tol_mm=0.01):
    """Затравочное кольцо — открытая граница каркаса, кроме шва.

    У половины детали открытых границ две по природе: торец и сам шов. Шов
    отбрасывается по координате, торец остаётся. Если торцов несколько,
    затравку выбирает исполнитель.
    """
    mm = mm_per_unit()
    ai = _NORMAL[seam_axis]
    def on_seam(e):
        return all(abs(v.co[ai] * mm) < seam_tol_mm for v in e.verts)
    edges = [e for e in bm.edges if len(e.link_faces) == 1 and not on_seam(e)]
    if not edges:
        return None, "открытых границ, кроме шва, нет"
    # Связность считается по САМИМ граничным рёбрам. Обход по всем рёбрам
    # вершины ушёл бы внутрь сетки и слил бы все границы в одну.
    nb = {}
    for e in edges:
        a, b = e.verts
        nb.setdefault(a, []).append(b)
        nb.setdefault(b, []).append(a)
    seen, comps = set(), []
    for v in nb:
        if v in seen:
            continue
        comp, stack = [], [v]
        while stack:
            w = stack.pop()
            if w in seen:
                continue
            seen.add(w)
            comp.append(w)
            stack.extend(x for x in nb[w] if x not in seen)
        comps.append(comp)
    if len(comps) != 1:
        return None, "открытых границ несколько: %d" % len(comps)
    return set(comps[0]), None


def rings(ob, count=40, seed_z_mm=None, seed_tol_mm=0.6,
          seam_axis="X", seam_tol_mm=0.01):
    """Кольца каркаса **по числу рёбер** от затравки, а не по координате.

    Отбор ряда по координате держится ровно до первой наклонной петли: как
    только кольцо перестаёт быть плоским, его координата совпадает с чужой, и
    ряд собирается из кусков двух разных колец. Проверено на живой сетке —
    ряд из тринадцати вершин пришёл четырнадцатью и с тремя концами.

    Признак кольца — расстояние в рёбрах от известной границы. Он не зависит
    от того, куда уехали вершины, и переживает любую формовку.

    Возвращает список списков **индексов вершин**, от затравки вглубь; каждое
    кольцо уже упорядочено обходом (см. :func:`ring_order`). Индексы, а не
    ``BMVert``: ссылки на элементы освобождённого bmesh недействительны, и
    обращение к ним роняет весь вызов.
    """
    mm = mm_per_unit()
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    try:
        if seed_z_mm is None:
            cur, err = _seed_ring(bm, seam_axis, seam_tol_mm)
            if cur is None:
                raise ValueError("затравку не выбрать: %s; задай seed_z_mm" % err)
        else:
            cur = set(v for v in bm.verts
                      if abs(v.co.z * mm - seed_z_mm) < seed_tol_mm)
            if not cur:
                raise ValueError("на высоте %.1f вершин нет" % seed_z_mm)
        seen, out = set(cur), []
        while cur and len(out) < count:
            out.append(cur)
            nxt = set()
            for v in cur:
                for e in v.link_edges:
                    w = e.other_vert(v)
                    if w not in seen:
                        nxt.add(w)
            seen |= nxt
            cur = nxt
        return [[v.index for v in (_order(bm, r) or sorted(r, key=lambda v: v.index))]
                for r in out]
    finally:
        bm.free()


def _order(bm, rowset):
    """Обход кольца по связности: от переднего конца к заднему.

    Замкнутое кольцо и кольцо-путь различаются числом концов. У половины
    детали кольцо, пересекающее шов, — путь с двумя концами на плоскости
    симметрии; кольцо, шва не касающееся, замкнуто.
    """
    nb = {v: [w for e in v.link_edges
              for w in (e.other_vert(v),) if w in rowset] for v in rowset}
    ends = [v for v in rowset if len(nb[v]) == 1]
    if len(ends) == 2:
        start = min(ends, key=lambda v: v.co.y)
    elif not ends and rowset:
        start = min(rowset, key=lambda v: v.co.y)    # замкнутое: начало по переду
    else:
        return None                                   # ветвление — не кольцо
    order, prev, cur = [start], None, start
    while True:
        nxt = [w for w in nb[cur] if w is not prev and w not in order]
        if not nxt:
            break
        prev, cur = cur, nxt[0]
        order.append(cur)
    return order if len(order) == len(rowset) else None


def ring_order(ob, idx, **kw):
    """Индексы вершин одного кольца по порядку обхода."""
    return rings(ob, count=idx + 1, **kw)[idx]


def place_ring(ob, idx, half_w_mm, front_mm, back_mm,
               z_mm=None, z_fn=None, phis=None, n_front=2.0, n_back=2.0, **kw):
    """Посадить кольцо ``idx`` на эллипс с равным шагом по дуге.

    ``z_fn`` получает долю пути вдоль кольца (0 — перёд, 1 — зад) и возвращает
    высоту в миллиметрах: так задаётся **наклонная** петля, без которой
    поднутрение не построить. ``z_mm`` — плоское кольцо. Ни одного —
    высоты вершин остаются как есть.
    """
    mm = mm_per_unit()
    order = ring_order(ob, idx, **kw)
    n = len(order)
    pts = ring_positions(half_w_mm, front_mm, back_mm, n, phis=phis,
                         n_front=n_front, n_back=n_back)
    me = ob.data
    for k, (vi, (x, y)) in enumerate(zip(order, pts)):
        v = me.vertices[vi]
        z = v.co.z * mm
        if z_fn is not None:
            z = z_fn(k / (n - 1)) if n > 1 else z_fn(0.0)
        elif z_mm is not None:
            z = z_mm
        v.co = (x / mm, y / mm, z / mm)
    me.update()
    return {"кольцо": idx, "вершин": n}


def crease_arc(ob, idx, k0, k1, weight, **kw):
    """Складка на рёбрах кольца с ``k0`` по ``k1`` — доля обхода от переда к заду.

    Кольцо охватывает деталь целиком, а край живёт лишь на части обхода.
    Складка на **всё** кольцо даёт ребро по всему обводу: проверено дважды —
    на верхе плеча она дала гребень по груди и спине, на линии белья ребро
    вокруг бёдер. Оба раза числа были в допуске, а поверхность испорчена.

    Прочие рёбра этого кольца сбрасываются в ноль, чужие кольца не трогаются.
    """
    order = ring_order(ob, idx, **kw)
    все = {frozenset((order[k], order[k + 1])) for k in range(len(order) - 1)}
    нужные = {frozenset((order[k], order[k + 1]))
              for k in range(max(k0, 0), min(k1, len(order) - 1))}
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    lay = (bm.edges.layers.float.get("crease_edge")
           or bm.edges.layers.float.new("crease_edge"))
    n = 0
    for e in bm.edges:
        key = frozenset((e.verts[0].index, e.verts[1].index))
        if key in все:
            e[lay] = weight if key in нужные else 0.0
            if key in нужные:
                n += 1
    bm.to_mesh(me)
    me.update()
    bm.free()
    return {"кольцо": idx, "рёбер_в_складке": n, "вес": weight}


def extend(ob, z_mm, half_w_mm, front_mm, back_mm, phis=None, **kw):
    """Продолжение оболочки: вытяжка открытой границы и посадка нового кольца.

    Плотность не добавляет — тест плотности (11.4) к ней не применяется.
    """
    mm = mm_per_unit()
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    seed, err = _seed_ring(bm)
    if seed is None:
        bm.free()
        raise ValueError("затравку не выбрать: %s" % err)
    edges = [e for e in bm.edges
             if len(e.link_faces) == 1 and e.verts[0] in seed and e.verts[1] in seed]
    res = bmesh.ops.extrude_edge_only(bm, edges=edges)
    new = [g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)]
    for v in new:
        v.co.z = z_mm / mm
    bm.to_mesh(me)
    me.update()
    bm.free()
    place_ring(ob, 0, half_w_mm, front_mm, back_mm, z_mm=z_mm, phis=phis, **kw)
    return {"вытянуто_рёбер": len(edges), "новых_вершин": len(new), "z": z_mm}


# ------------------------------------------------------------ замер образца

def ref_measure(empty, z_list_mm, thr=0.02, subpixel=False, seam_axis=None):
    """Габарит силуэта **самого образца** по пикселям подложки.

    Разметка — это чужой замер, снятый однажды и с одной трактовкой контура.
    Когда разметка спорит с картинкой, спор решает картинка; решать его надо
    числом, а не глазом на глазок.

    Две ловушки, обе проверены на живом образце:

    - **фон берётся построчно.** Один угловой пиксель на весь кадр не годится:
      при пороге 0.06 светлый край головы сливается с фоном, силуэт рвётся, и
      строка отдаёт обрезанный габарит, ничем не помеченный;
    - **порог низкий, около 0.02.** Он ловит и сглаживание края, поэтому
      габарит выходит на один-два пикселя шире истинного. Это смещение
      одностороннее и его надо помнить при сверке.

    Поле ``разрывов`` — число пикселей внутри габарита, не отличившихся от
    фона. Ненулевое значит, что силуэт распался и строке верить нельзя.
    """
    mm = mm_per_unit()
    img = empty.data
    if img is None:
        raise ValueError("у пустышки «%s» нет картинки" % empty.name)
    w, h = img.size
    px = list(img.pixels)
    big = float(max(w, h))
    sx = empty.empty_display_size * w / big
    sy = empty.empty_display_size * h / big
    ox, oy = empty.empty_image_offset
    m = empty.matrix_world
    o = m.translation
    ex = (m @ Vector((1.0, 0.0, 0.0)) - o)
    ey = (m @ Vector((0.0, 1.0, 0.0)) - o)
    if abs(ey.z) < 0.5:
        raise ValueError("подложка не вертикальна: local Y не смотрит в Z")
    ax = max(range(3), key=lambda i: abs(ex[i]))      # мировая ось подложки
    v0 = oy * sy                                       # низ картинки в local Y
    u0 = ox * sx
    out = {}
    for z in z_list_mm:
        v = ((z / mm) - o.z) / ey.z
        row = int(round((v - v0) / sy * h))
        if not (0 <= row < h):
            out[z] = None
            continue
        i0 = (row * w) * 4
        bg = (px[i0], px[i0 + 1], px[i0 + 2])
        sig = []
        for c in range(w):
            i = (row * w + c) * 4
            sig.append(max(abs(px[i] - bg[0]), abs(px[i + 1] - bg[1]),
                           abs(px[i + 2] - bg[2])))
        cols = [c for c in range(w) if sig[c] > thr]
        if not cols:
            out[z] = None
            continue
        lo, hi = min(cols), max(cols)

        def world(c):
            u = u0 + (c + 0.5) * sx / w
            return (o[ax] + ex[ax] * u) * mm

        # Субпиксельный край — по умолчанию ВЫКЛЮЧЕН, и вот почему.
        #
        # Соблазн понятен: шаг в пиксель — это два миллиметра, и при таком шаге
        # пологая дуга неотличима от угла. Но приём работает только на резком
        # крае. У съёмочного образца край мягкий: свет рассеян, съёмка не
        # идеально в фокусе, и сигнал нарастает не за пиксель, а за десяток.
        # Критерий «половина плато» тогда уезжает вглубь силуэта — проверено, в
        # шее обмер занизил ширину на сорок миллиметров, а в куполе завысил.
        #
        # Вывод общий: точность, которой нет в источнике, из него не
        # извлекается. Дугу на этом образце судит глаз (регламент, такт 4), а
        # обмер стережёт пропорции с той грубостью, какая есть.
        if subpixel and hi - lo > 8:
            inner = sorted(sig[lo + 3:hi - 2])
            plateau = inner[len(inner) // 2] if inner else max(sig)
            half = plateau * 0.5

            def edge(start, step):
                """Идти внутрь, пока сигнал не пересечёт половину плато."""
                c = start
                while 0 <= c < w and sig[c] < half:
                    c += step
                prev = c - step
                if not (0 <= c < w) or not (0 <= prev < w):
                    return float(start)
                a0, a1 = sig[prev], sig[c]
                if a1 == a0:
                    return float(c)
                return prev + (half - a0) / (a1 - a0) * step

            lo_f, hi_f = edge(lo, 1), edge(hi, -1)
        else:
            lo_f, hi_f = float(lo), float(hi)

        def world_f(cf):
            u = u0 + (cf + 0.5) * sx / w
            return (o[ax] + ex[ax] * u) * mm

        a, b = sorted((world_f(lo_f), world_f(hi_f)))
        out[z] = {"от": round(a, 2), "до": round(b, 2), "размах": round(b - a, 2),
                  "разрывов": (hi - lo + 1) - len(cols)}
    return {"подложка": empty.name, "ось": "XYZ"[ax],
            "мм_на_пиксель": round(empty.empty_display_size * mm / big, 4),
            "порог": thr, "строки": out}


# ---------------------------------------------------------------- оснастка

def guide(label, z_mm, width_mm, depth_mm, collection, depth_offset_mm=0.0):
    """Направляющая **на замер** (не на кольцо): пустышка-коробка, не геометрия.

    Направляющая принадлежит замеру; соответствие «замер = кольцо» не
    устанавливается ни на одной фазе. Пустышка не несёт полигонов, не попадает
    в подсчёт и в выдачу, и заблокирована от выделения.
    """
    mm = mm_per_unit()
    o = bpy.data.objects.new(f"РАЗМ_{label}", None)
    o.empty_display_type = "CUBE"
    o.empty_display_size = 1.0
    o.scale = (width_mm / 2 / mm, depth_mm / 2 / mm, 0.5 / mm)
    o.location = (0.0, depth_offset_mm / mm, z_mm / mm)
    o.show_in_front = True
    o.hide_select = True
    col = bpy.data.collections.get(collection)
    if col is None:
        col = bpy.data.collections.new(collection)
        bpy.context.scene.collection.children.link(col)
    col.objects.link(o)
    return {"направляющая": o.name, "коллекция": col.name}


# ---------------------------------------------------------------- показ

ANGLES = {
    "спереди": (90, 0, 0),
    "сзади": (90, 0, 180),
    "справа": (90, 0, 90),
    "слева": (90, 0, -90),
    "сверху": (0, 0, 0),
    "снизу": (180, 0, 0),
    "три_четверти": (65, 0, 45),
    "три_четверти_сзади": (65, 0, 135),
}

# English aliases. The toolkit grew in Russian and its identifiers stayed that
# way; renaming a proven tool to make its documentation prettier is a bad trade.
# Aliases cost nothing and let English callers use it without a phrasebook.
ANGLES.update({
    "front": ANGLES["спереди"],
    "back": ANGLES["сзади"],
    "right": ANGLES["справа"],
    "left": ANGLES["слева"],
    "top": ANGLES["сверху"],
    "bottom": ANGLES["снизу"],
    "three_quarter": ANGLES["три_четверти"],
    "three_quarter_back": ANGLES["три_четверти_сзади"],
})

# Обязательный набор для проверки правки кольца: габарит по двум видам, форма
# сечения сверху и облёт. Без вида сверху сечение не видно ни на одном ракурсе,
# и квадрат вместо овала живёт незамеченным.
#
# The mandatory set for checking a ring edit: the gauge from two views, the
# section's shape from above, and an orbit. Without the top view the section is
# invisible from every angle, and a box lives on where an oval was intended.
ПРОВЕРКА_КОЛЬЦА = ("сверху", "спереди", "справа")
RING_CHECK = ПРОВЕРКА_КОЛЬЦА
ОБЛЁТ = tuple(("облёт_%d" % a, (68, 0, a)) for a in (0, 60, 120, 180, 240, 300))
ORBIT = ОБЛЁТ

_CHANNEL_SAVED = {}


def frame_scale():
    """Масштаб кадра: сколько миллиметров приходится на пиксель снимка.

    **Без этого числа снимок нельзя отдавать на осмотр.** Осмотр меряет по
    пикселям, а перевести их в миллиметры может только тот, кто снимал.
    Угадывать нельзя: ``distance`` — это НЕ ширина кадра. При дистанции 200
    кадр выходит 288 мм в ширину, то есть в 1.44 раза шире.

    Проверено дорого: масштаб был сообщён заниженным в 1.44 раза, и разбор
    выдал девять «подтверждённых» находок, из которых главная — «шея тоньше
    образца на треть» — целиком порождена этой ошибкой. Состязательная
    проверка её не поймала: все линзы получили тот же неверный масштаб.

    Возвращает ``мм_на_пиксель`` и границы кадра. Для ортографических видов
    вдоль осей вертикаль кадра — это мировая Z, и границы по ней даны прямо.
    """
    mm = mm_per_unit()
    area, _ = _area3d()
    r3d = area.spaces.active.region_3d
    res = bpy.context.scene.render
    rx = int(res.resolution_x * res.resolution_percentage / 100)
    ry = int(res.resolution_y * res.resolution_percentage / 100)
    # Считается из ОБЪЕКТИВА и ДИСТАНЦИИ, а не из window_matrix: матрица окна
    # не пересчитывается до перерисовки и после смены вида отдаёт прежний кадр.
    # Проверено: сразу после view(distance=200) матрица всё ещё описывала кадр
    # предыдущего вызова, и масштаб выходил впятеро больше истинного.
    #
    # Соглашение Blender: поле объектива задано «сенсором» 36 мм по ПОЛОВИНЕ
    # большей стороны кадра.
    lens = area.spaces.active.lens
    большая = 2.0 * (36.0 / lens) * r3d.view_distance * mm
    mmpp = большая / max(rx, ry)
    ширина = mmpp * rx
    c = [v * mm for v in r3d.view_location]
    return {"мм_на_пиксель": round(mmpp, 5),
            "кадр_мм": [round(ширина, 1), round(ry * mmpp, 1)],
            "снимок_px": [rx, ry],
            "центр_мм": [round(v, 1) for v in c],
            "Z_верх": round(c[2] + ry * mmpp / 2, 1),
            "Z_низ": round(c[2] - ry * mmpp / 2, 1),
            "дистанция_мм": round(r3d.view_distance * mm, 1)}


def _frame(ob, margin=1.25):
    """Наводка и дистанция, вмещающие деталь целиком.

    Нужна потому, что вид **не сбрасывается сам**: вызов без наводки оставляет
    камеру там, где её бросил предыдущий. Общий план, снятый после крупного,
    молча выходит тем же крупным — картинка при этом выглядит исправной, а
    масштаб, указанный осмотру, оказывается ложным. Проверено: два снимка,
    заявленные как общий и крупный, совпали побайтово.
    """
    mm = mm_per_unit()
    b = bbox(ob)
    size = max(b["ширина_мм"], b["глубина_мм"], b["высота_мм"])
    return tuple(b["центр_мм"]), size * margin


def view(angle="три_четверти", ortho=True, focus=None, distance=None):
    """Поставить ракурс в **той же** области, из которой придёт снимок.

    Ортографии недостаточно, нужен поворот. Скриншот снимается отдельным
    инструментом MCP, не отсюда.
    """
    mm = mm_per_unit()
    area, n = _area3d()
    r3d = area.spaces.active.region_3d
    e = ANGLES[angle] if isinstance(angle, str) else angle
    r3d.view_perspective = "ORTHO" if ortho else "PERSP"
    r3d.view_rotation = Euler([math.radians(a) for a in e], "XYZ").to_quaternion()
    if focus is not None:
        r3d.view_location = Vector([c / mm for c in focus])
    if distance is not None:
        r3d.view_distance = distance / mm
    area.tag_redraw()
    return {"ракурс": angle, "перспектива": r3d.view_perspective,
            "областей_3d": n,
            "центр_мм": [round(c * mm, 1) for c in r3d.view_location],
            "дистанция_мм": round(r3d.view_distance * mm, 1)}


CHANNEL_ALIASES = {
    "working": "рабочий",
    "silhouette": "силуэт",
    "shading": "затенение",
    "wireframe": "каркас",
    "curvature": "кривизна",
}


def channel(name, ob=None):
    """Канал восприятия. ``"рабочий"`` возвращает как было.

    - ``силуэт`` / ``silhouette`` — плоская заливка одним цветом, оверлеи выключены;
    - ``затенение`` / ``shading`` — гладкое затенение простым материалом;
    - ``каркас`` / ``wireframe`` — каркас поверх сглаженного результата;
    - ``кривизна`` / ``curvature`` — полосатый матовый материал: показывает разрыв
      кривизны при нулевой ошибке положения.

    English names are accepted as aliases for every channel.
    """
    name = CHANNEL_ALIASES.get(name, name)
    area, _ = _area3d()
    sp = area.spaces.active
    sh, ov = sp.shading, sp.overlay
    if "shading" not in _CHANNEL_SAVED:
        _CHANNEL_SAVED["shading"] = (sh.type, sh.light, sh.color_type,
                                     tuple(sh.single_color), ov.show_overlays)
    if name == "рабочий":
        # Явное известное состояние, а не «что сохранилось». Сохранённое можно
        # отравить: если первый вызов channel() случился уже после переключения,
        # в него попадёт изменённое состояние — и «рабочий» вернёт не то. Так и
        # вышло: оверлеи оказались выключены, а вместе с ними пропали образцы,
        # потому что пустышки-изображения рисуются оверлеями. Наложение
        # перестало быть наложением, оставаясь на вид исправным снимком.
        sh.type, sh.light, sh.color_type = "SOLID", "STUDIO", "MATERIAL"
        sh.background_type = "THEME"
        ov.show_overlays = True
        if ob is not None:
            ob.show_wire = False
    elif name == "силуэт":
        # Белое на чёрном, а не почти чёрное на тёмно-сером: при низком контрасте
        # затенённая сторона сливается с фоном, и контур пропадает именно там, где
        # его меряют. Проверено — на этом ошибся разбор.
        sh.type, sh.light, sh.color_type = "SOLID", "FLAT", "SINGLE"
        sh.single_color = (1.0, 1.0, 1.0)
        sh.background_type = "VIEWPORT"
        sh.background_color = (0.0, 0.0, 0.0)
        ov.show_overlays = False
    elif name == "затенение":
        sh.type, sh.light, sh.color_type = "SOLID", "STUDIO", "SINGLE"
        sh.single_color = (0.55, 0.55, 0.55)
        ov.show_overlays = False
        if ob is not None and ob.type == "MESH" and ob.mode == "OBJECT":
            me = ob.data
            me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
            me.update()
    elif name == "кривизна":
        # Отражающий канал. Рассеянный серый показывает ПОЛОЖЕНИЕ поверхности и
        # прячет её характер: излом кривизны при нулевой ошибке положения на нём
        # не виден вовсе. Проверено дорого — обвод шеи сошёлся с образцом до двух
        # миллиметров, а скорость его изменения ломалась в семнадцать раз, и ни
        # один осмотр по затенению этого не назвал.
        #
        # На зеркальном материале отражённая картина сжимается там, где кривизна
        # растёт, и ПЕРЕЛАМЫВАЕТСЯ там, где кривизна разрывна. Глаз ловит излом
        # отражения куда надёжнее, чем излом тона.
        sh.type, sh.light, sh.color_type = "SOLID", "MATCAP", "SINGLE"
        sh.single_color = (0.8, 0.8, 0.8)
        # Полосатый отражатель предпочтительнее гладкого зеркала: полоса —
        # это изофота, и её излом виден там, где на гладком отражении заметен
        # лишь плавный сдвиг тона.
        for mc in ("check_reflection_vertical.exr", "check_reflection_horizontal.exr",
                   "metal_carpaint.exr", "fullmetal.exr"):
            try:
                sh.studio_light = mc
                break
            except TypeError:
                continue
        ov.show_overlays = False
        if ob is not None and ob.type == "MESH" and ob.mode == "OBJECT":
            me = ob.data
            me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
            me.update()
    elif name == "каркас":
        sh.type, sh.light, sh.color_type = "SOLID", "STUDIO", "SINGLE"
        sh.single_color = (0.55, 0.55, 0.55)
        ov.show_overlays = True
        if ob is not None:
            ob.show_wire = True
            ob.show_all_edges = True
            for m in ob.modifiers:
                if m.type == "SUBSURF":
                    m.show_on_cage = True
    else:
        raise KeyError(f"канал «{name}» не описан; есть: силуэт, затенение, "
                       f"кривизна, каркас, рабочий")
    area.tag_redraw()
    return {"канал": name, "затенение": sh.type, "свет": sh.light,
            "оверлеи": ov.show_overlays}


def orbit(name, directory, chan="затенение", ob=None, focus=None, distance=None):
    """Облёт вокруг детали: шесть ракурсов через 60°.

    Осмотр с вращением, которого требует такт 4, для правки кольца исполняется
    именно так: неверная посадка вершины видна не с любого угла.
    """
    os.makedirs(directory, exist_ok=True)
    scene = bpy.context.scene
    saved = (scene.render.filepath, scene.render.image_settings.file_format)
    scene.render.image_settings.file_format = "PNG"
    channel(chan, ob)
    if focus is None and distance is None and ob is not None:
        focus, distance = _frame(ob)      # кадр не наследуется, см. _frame
    made = []
    try:
        area, _ = _area3d()
        region = next(r for r in area.regions if r.type == "WINDOW")
        for label, e in ОБЛЁТ:
            view(e, focus=focus, distance=distance)
            path = os.path.join(directory, f"{name}_{label}.png")
            scene.render.filepath = path
            with bpy.context.temp_override(area=area, region=region,
                                           space_data=area.spaces.active):
                bpy.ops.render.opengl(view_context=True, write_still=True)
            made.append(path)
        масштаб = frame_scale()
    finally:
        scene.render.filepath, scene.render.image_settings.file_format = saved
    return {"снимки": made, "ракурсов": len(ОБЛЁТ), "масштаб": масштаб}


def shots(name, directory, angles=("спереди", "справа", "три_четверти"),
          chan="затенение", ob=None, focus=None, distance=None):
    """Набор снимков рабочего вида — картинки «до» и «после» для сравнения.

    Снимается **вьюпорт**, а не камера: рендер камерой — это её настройки, а не
    то, что видит исполнитель.

    ``focus`` и ``distance`` дают **крупный план зоны операции**, без которого
    осмотр не проверка. Дефект величиной в доли миллиметра на кадре, где деталь
    занимает седьмую часть высоты, не виден никому — ни человеку, ни разбору.

    Опущены — кадр **выставляется по детали заново**, а не наследуется. Иначе
    общий план, снятый после крупного, молча остаётся крупным.
    """
    os.makedirs(directory, exist_ok=True)
    scene = bpy.context.scene
    saved = (scene.render.filepath, scene.render.image_settings.file_format)
    scene.render.image_settings.file_format = "PNG"
    channel(chan, ob)
    if focus is None and distance is None and ob is not None:
        focus, distance = _frame(ob)
    made = []
    try:
        area, _ = _area3d()
        region = next(r for r in area.regions if r.type == "WINDOW")
        for a in angles:
            view(a, focus=focus, distance=distance)
            path = os.path.join(directory, f"{name}_{a}.png")
            scene.render.filepath = path
            with bpy.context.temp_override(area=area, region=region,
                                           space_data=area.spaces.active):
                bpy.ops.render.opengl(view_context=True, write_still=True)
            made.append(path)
        масштаб = frame_scale()
    finally:
        scene.render.filepath, scene.render.image_settings.file_format = saved
    # Масштаб отдаётся ВСЕГДА: снимок без него нельзя передать на осмотр.
    return {"снимки": made, "канал": chan, "масштаб": масштаб}


# ---------------------------------------------------------------- откат

def snapshot(name, directory):
    """Точка отката: копия файла. Текущий путь работы не меняется.

    ``relative_remap`` выключен намеренно: с ним пути к образцам
    пересчитываются относительно каталога точек, и восстановленный файл теряет
    их, оставаясь на вид целым.
    """
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{name}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True,
                                check_existing=False, relative_remap=False,
                                compress=False)
    return {"точка": name, "путь": path, "байт": os.path.getsize(path),
            "текущий_файл": bpy.data.filepath}


def restore(path, work_file=None, directory=None, keep_as=None):
    """Вернуться на точку. Текущее состояние сначала сохраняется отдельно.

    Откат возвращает точку **целиком**; выборочный откат отдельных вершин
    запрещён. Шаги после точки переигрываются.

    ``work_file`` — путь рабочего файла. Он обязателен по смыслу: открытие
    точки делает рабочим файлом **саму точку**, и все последующие сохранения
    молча уходят в каталог точек, а рабочий файл остаётся на состоянии до
    отката. Проверено опытом. Если путь передан, сессия сразу сохраняется в
    него, и работа продолжается там, где шла.

    После открытия файла модуль ``pp`` в сессии остаётся — Blender не
    перезапускается (проверено), — но все ссылки на объекты, взятые до отката,
    недействительны: брать заново через :func:`obj`.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"точки «{path}» нет; доступные: {points(directory)}")
    kept = None
    if directory and keep_as:
        kept = snapshot(keep_as, directory)["путь"]
    bpy.ops.wm.open_mainfile(filepath=path, load_ui=False)
    out = {"возврат_на": path, "прежнее_состояние_сохранено": kept,
           "внимание": "ссылки на объекты, взятые до отката, недействительны"}
    if work_file:
        bpy.ops.wm.save_as_mainfile(filepath=work_file, check_existing=False,
                                    relative_remap=False)
        out["рабочий_файл"] = bpy.data.filepath
    else:
        out["ВНИМАНИЕ"] = (f"work_file не передан: рабочим файлом стал «{bpy.data.filepath}», "
                           f"дальнейшие сохранения уйдут туда")
    return out


def points(directory):
    """Список доступных точек отката: по нему выбирается, куда возвращаться."""
    if not directory or not os.path.isdir(directory):
        return []
    out = []
    for f in sorted(os.listdir(directory)):
        if f.endswith(".blend"):
            p = os.path.join(directory, f)
            out.append({"точка": f[:-6], "путь": p, "байт": os.path.getsize(p),
                        "время": os.path.getmtime(p)})
    return out
