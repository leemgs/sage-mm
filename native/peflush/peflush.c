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
// and validate Private_Clean accounting via /proc/self/smaps.

static int is_candidate_line(const char* line) {
    // Example line: 7f2b4c...-... r--p 00000000 08:01 123456 /usr/lib/.../Some.dll
    const char *path = strchr(line, '/');
    return path != NULL &&
        (strstr(line, " r--p ") != NULL || strstr(line, " r-xp ") != NULL) &&
        strstr(path, " (deleted)") == NULL;
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

        // Apply MADV_DONTNEED
        errno = 0;
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
    if (ok > 0) return ok;
    if (segments == 0) return 0;
    return -EIO;
}

// Optional: drop only mappings whose path contains a given substring
int peflush_drop_by_substring(const char* needle, int verbose) {
    if (!needle || !*needle) return -EINVAL;
    FILE* f = fopen("/proc/self/maps", "r");
    if (!f) return -errno;

    char line[4096];
    int ok=0, matched=0, last_error=0;
    while (fgets(line, sizeof(line), f)) {
        if (!strstr(line, needle)) continue;
        if (!is_candidate_line(line)) continue;
        unsigned long start=0, end=0;
        if (sscanf(line, "%lx-%lx", &start, &end) != 2) continue;
        size_t len = (size_t)(end - start);
        if (len == 0) continue;
        matched++;
        int dropped = madvise((void*)start, len, MADV_DONTNEED)==0;
        if (dropped) ok++; else last_error = errno;
        if (verbose) {
            fprintf(stderr, "[peflush/by] %s %p..%p\n", (dropped?"DROPPED":"SKIPPED"), (void*)start, (void*)end);
        }
    }
    fclose(f);
    if (ok > 0) return ok;
    if (matched == 0) return 0;
    return -(last_error ? last_error : EIO);
}

// Export friendly names for P/Invoke
__attribute__((visibility("default"))) int FlushCleanPages(int verbose) {
    return peflush_drop_clean_pages(verbose);
}
__attribute__((visibility("default"))) int FlushBySubstring(const char* needle, int verbose) {
    return peflush_drop_by_substring(needle, verbose);
}
