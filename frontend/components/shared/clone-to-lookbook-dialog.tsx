'use client';

import { useState } from 'react';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';
import { toast } from 'sonner';

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useCloneToLookbook } from '@/lib/hooks/use-studio';
import { getErrorMessage } from '@/lib/api';

interface CloneToLookbookDialogProps {
  open: boolean;
  sourceOutfitId: string;
  sourceOccasion: string;
  onClose: () => void;
  onSuccess?: (newOutfitId: string) => void;
}

import { OCCASIONS } from '@/lib/types';

function defaultCloneName(occasion: string): string {
  const occasionLabel =
    OCCASIONS.find((o) => o.value === occasion)?.label ??
    occasion.charAt(0).toUpperCase() + occasion.slice(1);
  return `${occasionLabel} — ${format(new Date(), 'd. MMM', { locale: de })}`;
}

export function CloneToLookbookDialog({
  open,
  sourceOutfitId,
  sourceOccasion,
  onClose,
  onSuccess,
}: CloneToLookbookDialogProps) {
  const [name, setName] = useState(() => defaultCloneName(sourceOccasion));
  const clone = useCloneToLookbook(sourceOutfitId);

  const handleConfirm = async () => {
    const trimmed = name.trim();
    if (!trimmed) {
      toast.error('Bitte gib einen Namen ein');
      return;
    }
    try {
      const result = await clone.mutateAsync({ name: trimmed });
      toast.success('Im Lookbook gespeichert');
      onSuccess?.(result.id);
      onClose();
    } catch (error) {
      toast.error(getErrorMessage(error, 'Speichern im Lookbook fehlgeschlagen'));
    }
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Im Lookbook speichern</DialogTitle>
          <DialogDescription>
            Gib diesem Look einen Namen, damit du ihn später wiederfindest und erneut tragen kannst.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-2 py-2">
          <Label htmlFor="lookbook-name">Name</Label>
          <Input
            id="lookbook-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={100}
            placeholder="Freitags-Brunch"
            autoFocus
          />
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={clone.isPending}>
            Abbrechen
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={clone.isPending || !name.trim()}
          >
            {clone.isPending ? 'Wird gespeichert...' : 'Speichern'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
