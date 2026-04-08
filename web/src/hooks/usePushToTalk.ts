import { useCallback, useState } from 'react';
import { useMicrophone } from './useMicrophone';

export function usePushToTalk(args: {
  onBegin?: () => void;
  onChunk: (audio: string, sampleRate: number) => void;
  onStop: () => void;
}) {
  const microphone = useMicrophone();
  const [busy, setBusy] = useState(false);

  const begin = useCallback(async () => {
    setBusy(true);
    args.onBegin?.();
    await microphone.start((audio) => args.onChunk(audio, microphone.sampleRate));
  }, [args, microphone]);

  const end = useCallback(async () => {
    await microphone.stop();
    args.onStop();
    setBusy(false);
  }, [args, microphone]);

  return {
    begin,
    end,
    busy,
    recording: microphone.recording,
    error: microphone.error,
  };
}
