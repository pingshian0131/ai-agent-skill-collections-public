#!/usr/bin/env bash
set -euo pipefail

QUERY="${1:?Usage: lookup_contact.sh <search_term>}"

osascript - "$QUERY" <<'APPLESCRIPT'
on run argv
    set searchTerm to item 1 of argv
    tell application "Contacts"
        set matchingPeople to (every person whose name contains searchTerm)
        -- Also search by nickname
        set nickMatches to (every person whose nickname contains searchTerm)
        -- Merge (deduplicate by checking id)
        repeat with p in nickMatches
            set pid to id of p
            set found to false
            repeat with m in matchingPeople
                if id of m = pid then set found to true
            end repeat
            if not found then set end of matchingPeople to p
        end repeat

        if (count of matchingPeople) = 0 then
            return "NO_MATCH"
        end if

        set output to ""
        repeat with p in matchingPeople
            set pName to name of p
            set pNick to ""
            try
                set pNick to nickname of p as text
                if pNick = "missing value" then set pNick to ""
            end try
            set pPhones to ""
            repeat with ph in (phones of p)
                if pPhones ≠ "" then set pPhones to pPhones & ","
                set pPhones to pPhones & (value of ph)
            end repeat
            set pEmails to ""
            repeat with em in (emails of p)
                if pEmails ≠ "" then set pEmails to pEmails & ","
                set pEmails to pEmails & (value of em)
            end repeat
            set output to output & pName & " | " & pNick & " | " & pPhones & " | " & pEmails & linefeed
        end repeat
        return output
    end tell
end run
APPLESCRIPT
