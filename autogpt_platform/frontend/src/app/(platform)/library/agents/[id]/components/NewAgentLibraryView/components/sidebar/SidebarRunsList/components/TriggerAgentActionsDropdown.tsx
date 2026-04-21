"use client";

import type { LibraryAgent } from "@/app/api/__generated__/models/libraryAgent";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/molecules/DropdownMenu/DropdownMenu";
import { DotsThreeVerticalIcon } from "@phosphor-icons/react";
import Link from "next/link";
import { useRemoveTriggerAgent } from "../../../../hooks/useRemoveTriggerAgent";

interface Props {
  parentAgent: LibraryAgent;
  triggerAgent: LibraryAgent;
  onDeleted?: () => void;
}

export function TriggerAgentActionsDropdown({
  parentAgent,
  triggerAgent,
  onDeleted,
}: Props) {
  const { openDialog, dialog } = useRemoveTriggerAgent({
    parentAgent,
    triggerAgent,
    onDeleted,
  });

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button
            className="ml-auto shrink-0 rounded p-1 hover:bg-gray-100"
            onClick={(e) => e.stopPropagation()}
            aria-label="More actions"
          >
            <DotsThreeVerticalIcon className="h-5 w-5 text-gray-400" />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem asChild>
            <Link
              href={`/library/agents/${triggerAgent.id}`}
              onClick={(e) => e.stopPropagation()}
            >
              View in library
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem asChild>
            <Link
              href={`/build?flowID=${triggerAgent.graph_id}`}
              onClick={(e) => e.stopPropagation()}
            >
              Open in builder
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={(e) => {
              e.stopPropagation();
              openDialog();
            }}
          >
            Remove trigger
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      {dialog}
    </>
  );
}
