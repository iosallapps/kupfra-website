// kupfra.com: one fade-up per section. Nothing here is required to read the page;
// without this file every section is visible.
(function () {
    "use strict";
    var items = document.querySelectorAll(".reveal");
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce || !("IntersectionObserver" in window)) {
        for (var i = 0; i < items.length; i++) { items[i].classList.add("is-in"); }
        return;
    }
    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-in");
                observer.unobserve(entry.target);
            }
        });
    }, { rootMargin: "0px 0px -8% 0px" });
    for (var j = 0; j < items.length; j++) { observer.observe(items[j]); }
})();
