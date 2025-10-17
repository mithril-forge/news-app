'use client';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '~/components/ui/select';
import { ArrowUpDown } from 'lucide-react';

export type SortOption = 'relevance' | 'latest';

interface SortDropdownProps {
  currentSort: SortOption;
  onSortChange: (sort: SortOption) => void;
  className?: string;
  disabled?: boolean;
}

const sortOptions: { value: SortOption; label: string }[] = [
  { value: 'relevance', label: 'Podle relevance' },
  { value: 'latest', label: 'Nejnovější' },
];

export default function SortDropdown({
  currentSort,
  onSortChange,
  className = '',
  disabled = false,
}: SortDropdownProps) {
  return (
    <Select
      value={currentSort}
      onValueChange={(value) => onSortChange(value as SortOption)}
      disabled={disabled}
    >
      <SelectTrigger className={`w-[180px] ${className}`}>
        <div className="flex items-center gap-2">
          <ArrowUpDown className="h-4 w-4 text-muted-foreground" />
          <SelectValue />
        </div>
      </SelectTrigger>
      <SelectContent>
        {sortOptions.map((option) => (
          <SelectItem key={option.value} value={option.value}>
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
