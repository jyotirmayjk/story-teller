import { useEffect, useRef } from 'react';

type AvatarState = 'idle' | 'listening' | 'processing' | 'speaking';

interface SpriteAvatarProps {
  src: string;
  state: AvatarState;
  label?: string;
  size?: number;
}

const FRAME_WIDTH = 256;
const FRAME_HEIGHT = 256;
const COLUMNS = 4;
const FPS = 6;

const animations: Record<AvatarState, number[]> = {
  idle: [0, 1, 2, 3],
  listening: [4, 5, 6, 7],
  processing: [8, 9, 10, 11],
  speaking: [12, 13, 14, 15],
};

export function SpriteAvatar({
  src,
  state,
  label = 'Assistant avatar',
  size = 128,
}: SpriteAvatarProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);
  const stateRef = useRef(state);

  useEffect(() => {
    stateRef.current = state;
  }, [state]);

  useEffect(() => {
    const image = new Image();
    image.src = src;
    imageRef.current = image;

    let animationIndex = 0;
    let lastFrameTime = 0;
    let frameRequest = 0;
    let isCancelled = false;

    const drawFrame = (time: number) => {
      if (isCancelled) {
        return;
      }

      const canvas = canvasRef.current;
      const ctx = canvas?.getContext('2d');
      const loadedImage = imageRef.current;
      if (!canvas || !ctx || !loadedImage?.complete) {
        frameRequest = requestAnimationFrame(drawFrame);
        return;
      }

      const sequence = animations[stateRef.current];
      if (time - lastFrameTime > 1000 / FPS) {
        animationIndex = (animationIndex + 1) % sequence.length;
        lastFrameTime = time;
      }

      const frame = sequence[animationIndex];
      const sx = (frame % COLUMNS) * FRAME_WIDTH;
      const sy = Math.floor(frame / COLUMNS) * FRAME_HEIGHT;

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(
        loadedImage,
        sx,
        sy,
        FRAME_WIDTH,
        FRAME_HEIGHT,
        0,
        0,
        canvas.width,
        canvas.height,
      );

      frameRequest = requestAnimationFrame(drawFrame);
    };

    frameRequest = requestAnimationFrame(drawFrame);

    return () => {
      isCancelled = true;
      cancelAnimationFrame(frameRequest);
    };
  }, [src]);

  return (
    <canvas
      ref={canvasRef}
      width={size}
      height={size}
      aria-label={`${label}: ${state}`}
      role="img"
      className="h-full w-full"
    />
  );
}
