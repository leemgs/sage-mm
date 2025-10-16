#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

// Very conservative per-process clean-page dropper.
// It scans /proc/self/maps and applies MADV_DONTNEED
// to readable, private, file-backed segments that look like PE/ELF text sections.
// This is a demo helper; production code should filter by module allowlists
// and validate 'clean' via mincore().

static int is_candidate_line(const char* line) {
    // Example line: 7f2b4c...-... r--p 00000000 08:01 123456 /usr/lib/.../Some.dll
    return strstr(line, " r--p ") != NULL || strstr(line, " r-xp ") != NULL;
}

int peflush_drop_clean_pages(int verbose) {
    FILE* f = fopen("/proc/self/maps", "r");
    if (!f) return -errno;

    char line[4096];
    int segments = 0, ok=0, fail=0;
    while (fgets(line, sizeof(line), f)) {
        if (!is_candidate_line(line)) continue;

        // parse address range
        unsigned long start=0, end=0;
        if (sscanf(line, "%lx-%lx", &start, &end) != 2) continue;
        size_t len = (size_t)(end - start);
        if (len == 0) continue;

        // Skip anonymous mappings
        if (!strchr(line, '/')) continue;

        // Apply MADV_DONTNEED
        int r = madvise((void*)start, len, MADV_DONTNEED);
        segments++;
        if (r == 0) { ok++; }
        else { fail++; }

        if (verbose) {
            fprintf(stderr, "[peflush] %s -> %s (%p..%p, %zu bytes)\n",
                (strstr(line, " r-xp ") ? "text" : "rodata"),
                (r==0 ? "DROPPED" : "SKIPPED"),
                (void*)start, (void*)end, len);
        }
    }
    fclose(f);
    return (segments>0 && ok>0) ? ok : -1;
}

// Optional: drop only mappings whose path contains a given substring
int peflush_drop_by_substring(const char* needle, int verbose) {
    if (!needle || !*needle) return -EINVAL;
    FILE* f = fopen("/proc/self/maps", "r");
    if (!f) return -errno;

    char line[4096];
    int ok=0;
    while (fgets(line, sizeof(line), f)) {
        if (!strstr(line, needle)) continue;
        if (!strstr(line, " r--p ") && !strstr(line, " r-xp ")) continue;
        unsigned long start=0, end=0;
        if (sscanf(line, "%lx-%lx", &start, &end) != 2) continue;
        size_t len = (size_t)(end - start);
        if (len == 0) continue;
        if (madvise((void*)start, len, MADV_DONTNEED)==0) ok++;
        if (verbose) {
            fprintf(stderr, "[peflush/by] %s %p..%p\n", (ok?"DROPPED":"SKIPPED"), (void*)start, (void*)end);
        }
    }
    fclose(f);
    return ok>0 ? ok : -1;
}

// Export friendly names for P/Invoke
__attribute__((visibility("default"))) int FlushCleanPages(int verbose) {
    return peflush_drop_clean_pages(verbose);
}
__attribute__((visibility("default"))) int FlushBySubstring(const char* needle, int verbose) {
    return peflush_drop_by_substring(needle, verbose);
}
