// kupfra.com motion. Nothing here is needed to read the page: without this file every
// section is visible and every image is in place. Motion waits for prefers-reduced-motion.
(function () {
    "use strict";

    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
    var hasIO = "IntersectionObserver" in window;

    function onFrame(fn) {
        var queued = false;
        return function () {
            if (queued) { return; }
            queued = true;
            requestAnimationFrame(function () { queued = false; fn(); });
        };
    }

    // Header firms up after the first scroll.
    var header = document.querySelector(".site-header");
    if (header) {
        var setHeader = onFrame(function () { header.classList.toggle("is-scrolled", window.scrollY > 8); });
        window.addEventListener("scroll", setHeader, { passive: true });
        setHeader();
    }

    // Scroll reveals.
    var reveals = document.querySelectorAll(".reveal");
    if (reduce || !hasIO) {
        reveals.forEach(function (el) { el.classList.add("is-in"); });
    } else {
        var revealer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) { entry.target.classList.add("is-in"); revealer.unobserve(entry.target); }
            });
        }, { rootMargin: "0px 0px -8% 0px" });
        reveals.forEach(function (el) { revealer.observe(el); });
    }

    // Hero parallax: scroll moves the layers at their depth, the pointer tilts them a little.
    var stage = document.querySelector(".stage");
    if (stage && !reduce) {
        var layers = Array.prototype.slice.call(stage.querySelectorAll(".layer"));
        var px = 0, py = 0, tx = 0, ty = 0, visible = true, running = false;
        var paint = function () {
            tx += (px - tx) * 0.08;
            ty += (py - ty) * 0.08;
            var sy = Math.min(window.scrollY, 900);
            layers.forEach(function (layer) {
                var d = parseFloat(layer.getAttribute("data-depth")) || 0;
                layer.style.transform = "translate3d(" + (tx * d * 18).toFixed(2) + "px," + (ty * d * 14 - sy * d * 0.18).toFixed(2) + "px,0)";
            });
            if (visible && (Math.abs(px - tx) > 0.001 || Math.abs(py - ty) > 0.001)) {
                requestAnimationFrame(paint);
            } else { running = false; }
        };
        var kick = function () { if (!running && visible) { running = true; requestAnimationFrame(paint); } };
        window.addEventListener("scroll", onFrame(function () { if (visible) { paint(); } }), { passive: true });
        if (finePointer) {
            window.addEventListener("pointermove", function (e) {
                px = e.clientX / window.innerWidth - 0.5;
                py = e.clientY / window.innerHeight - 0.5;
                kick();
            }, { passive: true });
        }
        if (hasIO) {
            new IntersectionObserver(function (entries) { visible = entries[0].isIntersecting; if (visible) { kick(); } }).observe(stage);
        }
    }

    // Counters on the spec plate count up once, from zero.
    var counters = document.querySelectorAll("[data-count]");
    if (counters.length && !reduce && hasIO) {
        var counted = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) { return; }
                var el = entry.target, target = parseInt(el.getAttribute("data-count"), 10), start = null;
                counted.unobserve(el);
                var step = function (t) {
                    if (start === null) { start = t; }
                    var k = Math.min((t - start) / 1400, 1);
                    el.textContent = String(Math.round(target * (1 - Math.pow(1 - k, 3))));
                    if (k < 1) { requestAnimationFrame(step); }
                };
                el.textContent = "0";
                requestAnimationFrame(step);
            });
        }, { threshold: 0.6 });
        counters.forEach(function (el) { counted.observe(el); });
    }

    // Modules: the sticky phone shows the chapter in the middle of the screen.
    var chapters = document.querySelectorAll(".chapter[data-screen]");
    var moduleStage = document.querySelector(".module-stage");
    if (chapters.length && moduleStage && hasIO) {
        var screens = moduleStage.querySelectorAll(".screen img");
        var arts = moduleStage.querySelectorAll(".module-art img");
        var rail = moduleStage.querySelectorAll(".module-rail a");
        var show = function (i) {
            [screens, arts].forEach(function (list) {
                list.forEach(function (el, j) { el.classList.toggle("is-on", j === i); });
            });
            rail.forEach(function (el, j) { el.setAttribute("aria-current", j === i ? "true" : "false"); });
        };
        var chapterWatch = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) { show(parseInt(entry.target.getAttribute("data-screen"), 10)); }
            });
        }, { rootMargin: "-45% 0px -45% 0px" });
        chapters.forEach(function (el) { chapterWatch.observe(el); });
    }

    // Calculator tiles: tilt toward the pointer and carry a copper glow.
    if (finePointer && !reduce) {
        document.querySelectorAll(".tool").forEach(function (tile) {
            tile.addEventListener("pointermove", function (e) {
                var r = tile.getBoundingClientRect();
                var x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
                tile.style.setProperty("--ry", ((x - 0.5) * 10).toFixed(2) + "deg");
                tile.style.setProperty("--rx", ((0.5 - y) * 10).toFixed(2) + "deg");
                tile.style.setProperty("--gx", (x * 100).toFixed(1) + "%");
                tile.style.setProperty("--gy", (y * 100).toFixed(1) + "%");
            });
            tile.addEventListener("pointerleave", function () {
                tile.style.setProperty("--rx", "0deg");
                tile.style.setProperty("--ry", "0deg");
            });
        });
    }

    // Stair turntable: 48 pre-rendered frames on a canvas. It turns on its own while on screen
    // (unless motion is reduced) and follows a horizontal drag.
    var turn = document.querySelector(".turn-stage");
    if (turn && hasIO) {
        var canvas = turn.querySelector("canvas");
        var still = turn.querySelector("img");
        var ctx = canvas.getContext("2d");
        var count = parseInt(turn.getAttribute("data-frames"), 10);
        var buttons = document.querySelectorAll(".turn-controls button");
        var size = (turn.clientWidth * (window.devicePixelRatio || 1)) > 560 ? 760 : 420;
        canvas.width = canvas.height = size;
        var sets = {}, kind = "spiral", frame = 0, inView = false, dragging = false, lastX = 0, lastT = 0, acc = 0;

        var load = function (name) {
            if (sets[name]) { return sets[name]; }
            var list = [];
            for (var i = 0; i < count; i++) {
                var img = new Image();
                img.decoding = "async";
                img.src = "/img/turn/" + name + "-" + size + "-" + (i < 10 ? "0" : "") + i + ".webp";
                list.push(img);
            }
            sets[name] = list;
            return list;
        };
        var draw = function () {
            var list = sets[kind];
            if (!list) { return; }
            // Draw the nearest frame that has arrived, so a slow network never shows a gap.
            for (var k = 0; k < count; k++) {
                var img = list[(frame - k + count) % count];
                if (img.complete && img.naturalWidth) {
                    ctx.drawImage(img, 0, 0, size, size);
                    turn.classList.add("is-live");
                    return;
                }
            }
        };
        var tick = function (t) {
            if (!inView) { return; }
            if (!dragging && !reduce) {
                acc += lastT ? (t - lastT) : 0;
                if (acc > 70) { frame = (frame + 1) % count; acc = 0; draw(); }
            }
            lastT = t;
            requestAnimationFrame(tick);
        };
        new IntersectionObserver(function (entries) {
            var was = inView;
            inView = entries[0].isIntersecting;
            if (inView) {
                var list = load(kind);
                list[0].onload = draw;
                if (!was) { lastT = 0; requestAnimationFrame(tick); }
            }
        }, { rootMargin: "300px 0px" }).observe(turn);

        buttons.forEach(function (button) {
            button.addEventListener("click", function () {
                kind = button.getAttribute("data-kind");
                buttons.forEach(function (b) { b.setAttribute("aria-pressed", b === button ? "true" : "false"); });
                still.src = "/img/turn/" + kind + "-" + size + "-00.webp";
                still.removeAttribute("srcset");
                turn.classList.remove("is-live");
                var list = load(kind);
                list.forEach(function (img) { img.addEventListener("load", draw, { once: true }); });
                draw();
            });
        });

        turn.addEventListener("pointerdown", function (e) {
            dragging = true;
            lastX = e.clientX;
            turn.setPointerCapture(e.pointerId);
        });
        turn.addEventListener("pointermove", function (e) {
            if (!dragging) { return; }
            var step = turn.clientWidth / count * 0.9;
            var moved = Math.trunc((e.clientX - lastX) / step);
            if (moved !== 0) {
                frame = ((frame - moved) % count + count) % count;
                lastX += moved * step;
                draw();
            }
        });
        var release = function () { dragging = false; };
        turn.addEventListener("pointerup", release);
        turn.addEventListener("pointercancel", release);
    }
})();
